
import { Controller, Get } from '@nestjs/common';

@Controller('price')
export class PricesController {
  @Get()
  findAll(): string {
    return 'This action returns all prices';
  }
}
