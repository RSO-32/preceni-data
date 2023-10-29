import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule } from '@nestjs/config';
import { SellersController } from './sellers/sellers.controller';
import { BrandsController } from './brands/brands.controller';
import { PricesController } from './prices/prices.controller';
import { CategoriesController } from './categories/categories.controller';
import { ProductsController } from './products/products.controller';

@Module({
  imports: [
    ConfigModule.forRoot(),
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: process.env.DATABASE_HOSTNAME,
      port: parseInt(process.env.DATABASE_PORT),
      username: process.env.DATABASE_USER,
      password: process.env.DATABASE_PASSWORD,
      database: process.env.DATABASE_NAME,
      entities: ["dist/**/*.entity{.ts,.js}"],
      synchronize: true
    }),
  ],
  controllers: [AppController, SellersController, BrandsController, PricesController, CategoriesController, ProductsController],
  providers: [AppService],
})
export class AppModule {}
