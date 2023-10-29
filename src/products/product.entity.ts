import { Brand } from 'src/brands/brand.entity';
import { Category } from 'src/categories/category.entity';
import { Price } from 'src/prices/price.entity';
import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  ManyToOne,
  ManyToMany,
  OneToMany,
  JoinTable,
} from 'typeorm';
import { ProductToSeller } from './productToSeller.entity';

@Entity()
export class Product {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @ManyToOne(() => Brand, (brand) => brand.products)
  brand: Brand;

  @ManyToMany(() => Category)
  @JoinTable()
  categories: Category[];

  @OneToMany(() => Price, (price) => price.seller)
  prices: Price[];

  @OneToMany(
    () => ProductToSeller,
    (productToSeller) => productToSeller.product,
  )
  public sellers: ProductToSeller[];
}
