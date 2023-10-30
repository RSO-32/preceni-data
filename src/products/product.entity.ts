import { Brand } from 'src/brands/brand.entity';
import { Category } from 'src/categories/category.entity';
import { Price } from 'src/prices/price.entity';
import {
  Entity,
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

  @ManyToOne(() => Brand, (brand) => brand.products)
  brand: Brand;

  @ManyToMany(() => Category, { cascade: true })
  @JoinTable()
  categories: Category[];

  @OneToMany(() => Price, (price) => price.seller)
  prices: Price[];

  @OneToMany(
    () => ProductToSeller,
    (productToSeller) => productToSeller.product,
    { cascade: true },
  )
  public sellers: ProductToSeller[];

  name(): string {
    return this.sellers[0].name; // TODO: boljši način za določanje imena, vsak seller ima lahko svoje ime
  }
}
