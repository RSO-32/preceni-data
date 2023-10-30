import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Seller } from './seller.entity';
import { CreateSellerDTO } from './createSellerDTO';

@Injectable()
export class SellersService {
  constructor(
    @InjectRepository(Seller)
    private sellersRepository: Repository<Seller>,
  ) {}

  findAll(): Promise<Seller[]> {
    return this.sellersRepository.find();
  }

  findOne(id: number): Promise<Seller | null> {
    return this.sellersRepository.findOneBy({ id });
  }

  async remove(id: number): Promise<void> {
    await this.sellersRepository.delete(id);
  }

  async create(createSellerDTO: CreateSellerDTO): Promise<Seller> {
    Logger.log('Creating seller: ' + JSON.stringify(createSellerDTO));

    const seller = new Seller();
    seller.name = createSellerDTO.name;
    seller.website = createSellerDTO.website;

    return await this.sellersRepository.save(seller);
  }
}
