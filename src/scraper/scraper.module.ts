
import { Module } from '@nestjs/common';
import { ScraperService } from './scraper.service';
import { ScraperController } from './scraper.controller';
import { SellersModule } from 'src/sellers/sellers.module';
import { BrandsModule } from 'src/brands/brands.module';
import { CategoriesModule } from 'src/categories/categories.module';
import { ProductsModule } from 'src/products/products.module';

@Module({
  imports: [SellersModule, BrandsModule, CategoriesModule, ProductsModule],
  providers: [ScraperService],
  controllers: [ScraperController],
})
export class ScraperModule {}