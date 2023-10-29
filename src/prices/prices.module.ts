
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { PricesService } from './prices.service';
import { PricesController } from './prices.controller';
import { Price } from './price.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Price])],
  providers: [PricesService],
  controllers: [PricesController],
})
export class PricesModule {}