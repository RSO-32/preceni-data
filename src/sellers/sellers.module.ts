
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { SellersService } from './sellers.service';
import { SellersController } from './sellers.controller';
import { Seller } from './seller.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Seller])],
  providers: [SellersService],
  controllers: [SellersController],
  exports: [SellersService],
})
export class SellersModule {}