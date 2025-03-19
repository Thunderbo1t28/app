import axios from 'axios';

const authApi = {
  // ... existing code ...
  
  register: async (data: { username: string; email: string; password: string; password2: string }) => {
    const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    const url = `${baseUrl}/auth/register/`;
    console.log('Registration URL:', url);
    const response = await axios.post(url, data);
    return response.data;
  },
};

export default authApi; 