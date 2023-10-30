import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Category } from './category.entity';

@Injectable()
export class CategoriesService {
  constructor(
    @InjectRepository(Category)
    private categoriesRepository: Repository<Category>,
  ) {}

  findAll(): Promise<Category[]> {
    return this.categoriesRepository.find();
  }

  findOne(id: number): Promise<Category | null> {
    return this.categoriesRepository.findOneBy({ id });
  }

  async remove(id: number): Promise<void> {
    await this.categoriesRepository.delete(id);
  }

  async findOrCreate(names: string[]): Promise<Category[]> {
    const categories = [];
    for (const name of names) {
      Logger.log('Ensuring category: ' + name + ' exists');
      categories.push(
        await this.categoriesRepository.upsert({ name: name }, ['name']),
      );
    }

    return categories;
  }
}
