import { visionManifest } from '@/products/vision/manifest';
import type { ProductManifest } from './types/ProductManifest';

export const registeredProducts: ProductManifest[] = [
  visionManifest,
];

export function getProductById(id: string): ProductManifest | undefined {
  return registeredProducts.find(p => p.id === id);
}
