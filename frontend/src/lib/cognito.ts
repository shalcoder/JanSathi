import { Amplify } from 'aws-amplify';

export function configureAmplify() {
  const userPoolId = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID || '';
  const userPoolClientId = process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID || '';
  const hostedUiDomain = process.env.NEXT_PUBLIC_COGNITO_DOMAIN || '';
  const redirectSignIn = process.env.NEXT_PUBLIC_REDIRECT_SIGN_IN || '';
  const redirectSignOut = process.env.NEXT_PUBLIC_REDIRECT_SIGN_OUT || '';

  // Don't configure if env vars are missing (e.g. during SSR with no env)
  if (!userPoolId || !userPoolClientId) {
    console.warn('[Cognito] Missing NEXT_PUBLIC_COGNITO_USER_POOL_ID or NEXT_PUBLIC_COGNITO_CLIENT_ID — skipping Amplify.configure()');
    return;
  }

  const cognitoConfig: {
    userPoolId: string;
    userPoolClientId: string;
    signUpVerificationMethod: 'code';
    loginWith?: {
      oauth: {
        domain: string;
        scopes: string[];
        redirectSignIn: string[];
        redirectSignOut: string[];
        responseType: 'code';
      };
    };
  } = {
    userPoolId,
    userPoolClientId,
    signUpVerificationMethod: 'code',
  };

  // Only configure hosted-UI OAuth flow when full config is present.
  if (hostedUiDomain && redirectSignIn && redirectSignOut) {
    cognitoConfig.loginWith = {
      oauth: {
        domain: hostedUiDomain,
        scopes: ['email', 'openid', 'profile', 'aws.cognito.signin.user.admin'],
        redirectSignIn: [redirectSignIn],
        redirectSignOut: [redirectSignOut],
        responseType: 'code',
      },
    };
  }

  Amplify.configure({
    Auth: {
      Cognito: cognitoConfig,
    },
  });
}
