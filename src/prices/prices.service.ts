import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Price } from './price.entity';

@Injectable()
export class PricesService {
  constructor(
    @InjectRepository(Price)
    private pricesRepository: Repository<Price>,
  ) {}

  findAll(): Promise<Price[]> {
    return this.pricesRepository.find();
  }

  async remove(id: number): Promise<void> {
    await this.pricesRepository.delete(id);
  }
}
