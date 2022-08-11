from enum import Enum


class Region(str, Enum):
    Ohio = "us-east-2",
    NorthVirginia = "us-east-1",
    NorthCalifornia = "us-west-1",
    Oregon = "us-west-2",
    CapeTown = "af-south-1",
    HongKong = "ap-east-1",
    Mumbai = "ap-south-1",
    OsakaLocal = "ap-northeast-3",
    Seoul = "ap-northeast-2",
    Singapore = "ap-southeast-1",
    Sydney = "ap-southeast-2",
    Tokyo = "ap-northeast-1",
    CanadaCentral = "ca-central-1",
    Beijing = "cn-north-1",
    Ningxia = "cn-northwest-1",
    Frankfurt = "eu-central-1",
    Ireland = "eu-west-1",
    London = "eu-west-2",
    Milan = "eu-south-1",
    Paris = "eu-west-3",
    Stockholm = "eu-north-1",
    Bahrain = "me-south-1",
    SaoPaulo = "sa-east-1",
    USEast = "us-gov-east-1",
    USWest = "us-gov-west-1"


regions_full_names = {
    Region.Ohio: "us-east-2 (Ohio)",
    Region.NorthVirginia: "us-east-1 (N. Virginia)",
    Region.NorthCalifornia: "us-west-1 (N. California)",
    Region.Oregon: "us-west-2 (Oregon)",
    Region.CapeTown: "af-south-1 (Cape Town)",
    Region.HongKong: "ap-east-1 (Hong Kong)",
    Region.Mumbai: "ap-south-1 (Mumbai)",
    Region.OsakaLocal: "ap-northeast-3 (Osaka-Local)",
    Region.Seoul: "ap-northeast-2 (Seoul)",
    Region.Singapore: "ap-southeast-1 (Singapore)",
    Region.Sydney: "ap-southeast-2 (Sydney)",
    Region.Tokyo: "ap-northeast-1 (Tokyo)",
    Region.CanadaCentral: "ca-central-1 (Central)",
    Region.Beijing: "cn-north-1 (Beijing)",
    Region.Ningxia: "cn-northwest-1 (Ningxia)",
    Region.Frankfurt: "eu-central-1 (Frankfurt)",
    Region.Ireland: "eu-west-1 (Ireland)",
    Region.London: "eu-west-2 (London)",
    Region.Milan: "eu-south-1 (Milan)",
    Region.Paris: "eu-west-3 (Paris)",
    Region.Stockholm: "eu-north-1 (Stockholm)",
    Region.Bahrain: "me-south-1 (Bahrain)",
    Region.SaoPaulo: "sa-east-1 (São Paulo)",
    Region.USEast: "us-gov-east-1 (US-East)",
    Region.USWest: "us-gov-west-1 (US-West)"
}

platform_region_dict = {
    "America East": "us-east-1",
    "America West": "us-west-1",
    "Canada": "ca-central-1",
    "South America": "sa-east-1",
    "UK": "eu-west-2",
    "Ireland": "eu-west-1",
    "Germany": "eu-central-1",
    "France": "eu-west-3",
    "Sweden": "eu-north-1",
    "Italy": "eu-south-1",
    "Middle East": "me-south-1",
    "Africa": "af-south-1",
    "China": "cn-north-1",
    "Hong-Kong": "ap-east-1",
    "Japan": "ap-northeast-1",
    "Singapore": "ap-northeast-1",
    "South Korea": "ap-northeast-2",
    "India": "ap-south-1",
    "Australia": "ap-southeast-2",
    "GovCloud (US East)": "us-gov-east-1",
    "GovCloud (US West)": "us-gov-east-1"
}


def region_to_platform_region(region: str) -> str:
    return list(platform_region_dict.keys())[
        list(platform_region_dict.values()).index(
            region)]
