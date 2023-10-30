import { Injectable, Logger } from '@nestjs/common';
import { Seller } from 'src/sellers/seller.entity';
import { UpdateProductDTO } from './updateProductDTO';
import { Brand } from 'src/brands/brand.entity';
import { BrandsService } from 'src/brands/brands.service';
import { CategoriesService } from 'src/categories/categories.service';
import { ProductsService } from 'src/products/products.service';
import { Product } from 'src/products/product.entity';
import { createConnection } from 'net';
import { InjectDataSource } from '@nestjs/typeorm';
import { DataSource } from 'typeorm';

@Injectable()
export class ScraperService {
  constructor(
    private readonly brandsService: BrandsService,
    private readonly categoriesService: CategoriesService,
    private readonly productsService: ProductsService,
    @InjectDataSource()
    private dataSource: DataSource,
  ) {}

  updateOrCreate(seller: Seller, updateProductDTO: UpdateProductDTO) {
    if (!seller.products) this.createProduct(seller, updateProductDTO);
    else this.updateProduct(seller, updateProductDTO);
  }

  async createProduct(seller: Seller, updateProductDTO: UpdateProductDTO) {
    Logger.log('Creating product: ' + JSON.stringify(updateProductDTO));

    const brand = await this.brandsService.findOrCreate(updateProductDTO.brand);
    const categories = await this.categoriesService.findOrCreate(
      updateProductDTO.categories,
    );

    const product = new Product();
    product.brand = brand;
    product.categories = categories;

    this.dataSource.manager.save(product);
  }

  updateProduct(seller: Seller, updateProductDTO: UpdateProductDTO) {
    Logger.log('Updating product: ' + JSON.stringify(updateProductDTO));
  }
}
