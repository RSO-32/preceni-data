import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Brand } from './brand.entity';

@Injectable()
export class BrandsService {
  constructor(
    @InjectRepository(Brand)
    private brandsRepository: Repository<Brand>,
  ) {}

  findAll(): Promise<Brand[]> {
    return this.brandsRepository.find();
  }

  findOne(id: number): Promise<Brand | null> {
    return this.brandsRepository.findOneBy({ id });
  }

  async remove(id: number): Promise<void> {
    await this.brandsRepository.delete(id);
  }

  async findOrCreate(name: string): Promise<Brand> {
    const brand = await this.brandsRepository.findOneBy({ name: name });

    if (brand) {
      Logger.log('Found brand: ' + brand.name);
      return brand;
    }

    Logger.log('Creating brand: ' + name);
    const newBrand = new Brand();
    newBrand.name = name;
    this.brandsRepository.insert(newBrand);
    return await this.brandsRepository.findOneBy({ name: name });
  }
}
