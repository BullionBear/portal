from pydantic import BaseModel, Field, HttpUrl


class AppBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    description: str = Field(..., min_length=1, max_length=240)
    url: HttpUrl
    icon_url: HttpUrl | None = None
    category: str = Field(default="General", max_length=40)
    color: str = Field(default="#C4A35A", pattern=r"^#[0-9A-Fa-f]{6}$")
    order: int = Field(default=100, ge=0)
    enabled: bool = True


class AppCreate(AppBase):
    id: str = Field(..., min_length=1, max_length=40, pattern=r"^[a-z0-9][a-z0-9_-]*$")


class AppUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, min_length=1, max_length=240)
    url: HttpUrl | None = None
    icon_url: HttpUrl | None = None
    category: str | None = Field(default=None, max_length=40)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    order: int | None = Field(default=None, ge=0)
    enabled: bool | None = None


class App(AppBase):
    id: str


class PortalInfo(BaseModel):
    company: str
    tagline: str
