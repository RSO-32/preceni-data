
import { Controller, Get } from '@nestjs/common';

@Controller('brand')
export class BrandsController {
  @Get()
  findAll(): string {
    return 'This action returns all brands';
  }
}
