
import { Controller, Get } from '@nestjs/common';

@Controller('seller')
export class SellersController {
  @Get()
  findAll(): string {
    return 'This action returns all sellers';
  }
}
