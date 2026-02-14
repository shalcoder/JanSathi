import axios from 'axios';

export interface QueryResponse {
    query: string;
    answer: {
        text: string;
        audio: string;
    };
    context: string[];
    structured_sources?: {
        title: string;
        text: string;
        link: string;
        benefit: string;
        logo: string;
    }[];
    meta?: {
        language: string;
    };
}

export interface QueryRequest {
    text_query: string;
    language?: string;
    userId?: string;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

const apiClient = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const sendQuery = async (params: QueryRequest | FormData): Promise<QueryResponse> => {
    try {
        const response = await apiClient.post('/query', params, {
            headers: params instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : {}
        });
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

export const getHistory = async (limit: number = 10): Promise<any[]> => {
    try {
        const response = await apiClient.get(`/history?limit=${limit}`);
        return response.data;
    } catch (error) {
        console.error('History API Error:', error);
        return [];
    }
};

export const checkHealth = async (): Promise<boolean> => {
    try {
        const response = await apiClient.get('/health');
        return response.status === 200;
    } catch (error) {
        return false;
    }
};
export const analyzeImage = async (imageFile: File, language: string = 'hi'): Promise<any> => {
    try {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('language', language);
        formData.append('prompt', 'Explain this document simply and identify next steps.');

        const response = await apiClient.post('/analyze', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Analysis API Error:', error);
        throw error;
    }
};
export const getMarketRates = async (): Promise<any[]> => {
    try {
        const response = await apiClient.get('/market-rates');
        return response.data;
    } catch (error) {
        console.error('Market Rates API Error:', error);
        return [];
    }
};
