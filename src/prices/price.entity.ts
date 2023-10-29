import { Entity, Column, PrimaryColumn, ManyToOne } from 'typeorm';
import { Seller } from '../sellers/seller.entity';
import { Product } from '../products/product.entity';

@Entity()
export class Price {
  @Column({ type: 'timestamptz' })
  @PrimaryColumn()
  datetime: Date;

  @Column('decimal')
  price: number;

  @PrimaryColumn()
  sellerId: number;

  @ManyToOne(() => Seller, (seller) => seller.prices)
  seller: Seller;

  @PrimaryColumn()
  productId: number;

  @ManyToOne(() => Product, (product) => product.prices)
  product: Product;
}
