import axios from 'axios';

export interface QueryResponse {
    query: string;
    answer: {
        text: string;
        audio: string;
    };
    context: string[];
    meta?: {
        language: string;
    };
}

export interface QueryRequest {
    text_query: string;
    language?: string;
}

const apiClient = axios.create({
    headers: {
        'Content-Type': 'application/json',
    },
});

export const sendQuery = async (params: QueryRequest): Promise<QueryResponse> => {
    try {
        const response = await apiClient.post('/query', params);
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
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
