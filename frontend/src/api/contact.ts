import { api } from "./client";

export interface ContactData {
  name: string;
  email: string;
  type: string;
  subject: string;
  message: string;
}

export const contactApi = {
  sendContactEmail: async (data: ContactData) => {
    const response = await api.post("/contact", data);
    return response.data;
  },
};
