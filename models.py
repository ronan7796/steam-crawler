from pydantic import BaseModel, root_validator, Field
from typing import Dict


class GameInfos(BaseModel):
    title: str
    price: str
    discount_percent: str
    platform: str = Field(alias="drm")
    shop_links: str = Field(alias="link")

    @root_validator(pre=True)
    def parse_html(cls, values: Dict[str, str]):
        values["title"] = values["title"].text
        values["price"] = values["price"].text
        values["discount_percent"] = values["discount_percent"].text
        values["drm"] = values["drm"]['alt']
        values["link"] = values["link"]['href'].replace(
            "/us", "https://gg.deals")
        return values
