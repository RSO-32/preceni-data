import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule } from '@nestjs/config';
import { BrandsModule } from './brands/brands.module';
import { CategoriesModule } from './categories/categories.module';
import { PricesModule } from './prices/prices.module';
import { ProductsModule } from './products/products.module';
import { SellersModule } from './sellers/sellers.module';
import { ScraperModule } from './scraper/scraper.module';


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
      entities: ['dist/**/*.entity{.ts,.js}'],
      synchronize: true,
    }),
    BrandsModule,
    CategoriesModule,
    PricesModule,
    ProductsModule,
    SellersModule,
    ScraperModule
    ,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
