import { Product } from 'src/products/product.entity';
import { Entity, Column, PrimaryGeneratedColumn, OneToMany, Unique, Index} from 'typeorm';

@Entity()
export class Brand {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  @Unique(['name'])
  name: string;

  @OneToMany(() => Product, (product) => product.brand)
  products: Product[];
}
