import { Entity, Column, ManyToOne, PrimaryColumn } from 'typeorm';
import { Product } from './product.entity';
import { Seller } from '../sellers/seller.entity';

@Entity()
export class ProductToSeller {
  @Column()
  @PrimaryColumn()
  productId: number;

  @Column()
  @PrimaryColumn()
  sellerId: number;

  @Column()
  sellerProductId: string;

  @ManyToOne(() => Product, (product) => product.sellers)
  product: Product;

  @ManyToOne(() => Seller, (seller) => seller.products)
  seller: Seller;
}
