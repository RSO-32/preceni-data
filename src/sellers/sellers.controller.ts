import { Body, Controller, Get, Post } from '@nestjs/common';
import { SellersService } from './sellers.service';
import { CreateSellerDTO } from './createSellerDTO';
import { Seller } from './seller.entity';

@Controller('seller')
export class SellersController {
  constructor(private sellerService: SellersService) {}

  @Get()
  findAll(): string {
    return 'This action returns all sellers';
  }

  @Post()
  async create(@Body() createSellerDTO: CreateSellerDTO): Promise<Seller> {
    return await this.sellerService.create(createSellerDTO);
  }
}
