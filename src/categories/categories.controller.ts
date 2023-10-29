
import { Controller, Get } from '@nestjs/common';

@Controller('category')
export class CategoriesController {
  @Get()
  findAll(): string {
    return 'This action returns all categories';
  }
}
