export type ShippingMode = 'Easy Ship' | 'FBA' | 'Self Ship';
export type ServiceLevel = 'Premium' | 'Advanced' | 'Standard' | 'Basic';
export type ProductSize = 'Standard' | 'Heavy & Bulky';

export interface PricingFormData {
  category: string;
  price: number;
  weight: number;
  shipping_mode: ShippingMode;
  service_level: ServiceLevel;
  product_size: ProductSize;
  location: 'Local' | 'Regional' | 'National' | 'IXD';
}