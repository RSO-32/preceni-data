import { Body, Controller, Param, Post, Put } from '@nestjs/common';
import { SellersService } from 'src/sellers/sellers.service';
import { ScraperService } from './scraper.service';
import { UpdateProductDTO } from './updateProductDTO';

@Controller('scraper')
export class ScraperController {
  constructor(
    private readonly scraperService: ScraperService,
    private readonly sellersService: SellersService,
  ) {}

  @Put(':sellerId')
  updateOrCreate(
    @Param('sellerId') sellerId: number,
    @Body() updateProductDTOs: UpdateProductDTO[],
  ) {
    const seller = this.sellersService.findOne(sellerId).then((seller) => {
      for (const updateProductDTO of updateProductDTOs) {
        this.scraperService.updateOrCreate(seller, updateProductDTO);
      }
    });
  }
}
