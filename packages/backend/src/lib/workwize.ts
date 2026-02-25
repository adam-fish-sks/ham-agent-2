import axios from 'axios';

const WORKWIZE_API_BASE = 'https://prod-back.goworkwize.com/api/public';

export class WorkwizeClient {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  private async request(endpoint: string, params?: any) {
    try {
      const response = await axios.get(`${WORKWIZE_API_BASE}${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Accept': 'application/json',
        },
        params,
      });
      return response.data;
    } catch (error: any) {
      console.error(`Workwize API error (${endpoint}):`, error.response?.data || error.message);
      throw error;
    }
  }

  async getEmployees() {
    return this.request('/employees');
  }

  async getEmployee(id: string) {
    return this.request(`/employees/${id}`);
  }

  async getAssets() {
    return this.request('/assets');
  }

  async getAsset(id: string) {
    return this.request(`/assets/${id}`);
  }

  async getOrders() {
    return this.request('/orders');
  }

  async getOrder(id: string) {
    return this.request(`/orders/${id}`);
  }

  async getProducts() {
    return this.request('/products');
  }

  async getProduct(id: string) {
    return this.request(`/products/${id}`);
  }

  async getOffices() {
    return this.request('/offices');
  }

  async getOffice(id: string) {
    return this.request(`/offices/${id}`);
  }

  async getWarehouses() {
    return this.request('/warehouses');
  }

  async getWarehouse(id: string) {
    return this.request(`/warehouses/${id}`);
  }

  async getOffboards() {
    return this.request('/offboards');
  }

  async getOffboard(id: string) {
    return this.request(`/offboards/${id}`);
  }
}

export const workwizeClient = new WorkwizeClient(process.env.WORKWIZE_KEY!);
