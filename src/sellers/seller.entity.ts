import { Entity, Column, PrimaryGeneratedColumn, OneToMany } from 'typeorm';
import { Price } from '../prices/price.entity';
import { ProductToSeller } from 'src/products/productToSeller.entity';

@Entity()
export class Seller {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @Column()
  website: string;

  @OneToMany(() => Price, (price) => price.seller)
  prices: Price[];

  @OneToMany(
    () => ProductToSeller,
    (productToSeller) => productToSeller.seller,
    { cascade: true },
  )
  products: ProductToSeller[];
}
