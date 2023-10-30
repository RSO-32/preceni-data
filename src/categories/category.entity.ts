import { Entity, Column, PrimaryGeneratedColumn, ManyToMany, Unique } from 'typeorm';
import { Product } from '../products/product.entity';

@Entity()
export class Category {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  @Unique(['name'])
  name: string;

  @ManyToMany(() => Product)
  products: Product[];
}
