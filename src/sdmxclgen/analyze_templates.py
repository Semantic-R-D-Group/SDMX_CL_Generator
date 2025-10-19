# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Semantic R&D Group

# analyze_templates.py

# Lists and groups of SDMX and other agencies' codelists for analysis
# Used in analysis modules for matching and grouping codelists

SINGLE_CODELISTS = [
    "SDMX:CL_DECIMALS(1.0)", "SDMX:CL_UNIT_MULT(1.1)", "SDMX:CL_FREQ(2.1)",
    "UNSD:CL_COMMODITY(1.0)", "ESTAT:CL_REGIONAL(6.1.0)", "IMF:CL_ORGANISATION(1.14.0)", "ESTAT:CL_ITEM_PRICE(2.0)",
    "UIS:CL_EDUCATION_FIELD(1.0)", "IMF:CL_CURRENCY(1.6)", "UIS:CL_SECTOR(1.0)", "ESTAT:CL_IND_TYPE(1.1)",
    "ESTAT:CL_ENERGY_FLOWS(1.2)", "ESTAT:CL_WATER_FLOWS(1.0)", "ESTAT:CL_AIRPOL(1.3.0)",
    "SDMX:CL_TIME_FORMAT(1.0)", "SDMX:CL_BREAK_REASON(1.0)", "ESTAT:CL_MATURITY(1.8)",
     "ESTAT:CL_INTERACTORS(1.3)", "IMF:CL_GFSM_STO(1.0)",
    "UIS:CL_EDU_TABLEID(1.0)", "UIS:CL_EXPENDITURE_TYPE(1.0)",
    # Final
#    "ESTAT:CL_AP_DEFINITION(1.0)", "ESTAT:CL_BRIDGE_ITEM(1.3.0)", "ESTAT:CL_DEMAND_PROD(1.0)", "ESTAT:CL_EDP_WBB(1.0)", # Auto-tagging
    "ESTAT:CL_GFS_ECOFUNC(1.0)", "ESTAT:CL_GFS_TAXCAT(1.2)", "ESTAT:CL_NA_CONSOLIDAT(1.3)", "ESTAT:CL_NA_PRICES(1.1)",
    "ESTAT:CL_REF_PERIOD_DTL(1.0)", "ESTAT:CL_VALUATION(1.6)", "IAEG-SDGs:CL_NATURE(1.0)", "IAEG-SDGs:CL_REPORTING_TYPE(1.0)",
    "IMF:CL_ACCOUNT_ENTRY(1.5.0)", "IMF:CL_COMP_METHOD(1.2)", "IMF:CL_FUNCTIONAL_CAT(1.10.1)", "OECD:CL_FDI_RELATION(1.0)",
    "OECD:CL_MEASURE_PRINCIP(1.0)", "SDMX:CL_CIVIL_STATUS(1.0)", "SDMX:CL_CONF_STATUS(1.3)", "SDMX:CL_TIMETRANS_TYPE(1.0)",
    "UIS:CL_GRADE(1.0)", "UIS:CL_ORIGIN_CRITERION(1.0)", "UNSD:CL_PARTNER_TYPE(1.0)", "UNSD:CL_TRADE_FLOW(1.0)",
#    "UNSD:CL_TRADE_SYSTEM(1.0)",   # Auto-tagging
    # "", "", "", "",
    ]



# Grouping of codelists by thematic categories for intersection analysis and semantic matching
GROUP_CODELISTS = {
    "activity": {"name": "Activities", "codelists": ["UNSD:CL_ACTIVITY(1.0)", "SDMX:CL_ACTIVITY_ISIC4(1.0)",
                                                      "SDMX:CL_ACTIVITY_ANZSIC06(1.0)", "SDMX:CL_ACTIVITY_NACE2(1.0)",
                                                      "OECD:CL_ACTIVITY_ALLOC(1.0)", "ESTAT:CL_ACTIVITY93(1.6)",
                                                      "ESTAT:CL_ACTIVITY(1.11.0)", "IAEG-SDGs:CL_ACTIVITY(1.6)"]},
    "age": {"name": "Age", "codelists": ["IAEG-SDGs:CL_AGE(1.19)", "UIS:CL_AGE(1.0)"]}, # Split into 2 CL - different subject
    "ageUnit": {"name": "Units of Age Measurement", "codelists": ["SDMX:CL_AGE(1.0)"]},
    "seasonalAdjust": {"name": "Adjustment indicator", "codelists": ["SDMX:CL_SEASONAL_ADJUST(1.0)",
                                                            "ESTAT:CL_SEASON_ADJUST(1.0)", "ESTAT:CL_ADJUSTMENT(1.4)",
                                                            "IMF:CL_ADJUSTMENT(1.4)"]},
    "area": {"name": "Countries", "codelists": ["SDMX:CL_AREA(2.0.1)", "ESTAT:CL_AREA(1.8)",
                                                     "IAEG-SDGs:CL_AREA(1.17)", "IMF:CL_AREA(1.17.0)", "UIS:CL_AREA(1.0)",
                                                     "UNSD:CL_AREA(1.0)"]},
    "custom": {"name": "Custom code",
               "codelists": ["ESTAT:CL_CUST_BREAKDOWN(1.6.0)", "IAEG-SDGs:CL_CUST_BREAKDOWN(1.14)"]},
    "assets": {"name": "Instrument and Assets", "codelists": ["ESTAT:CL_INSTR_ASSET(1.14.0)", "ESTAT:CL_INSTR_ASSET93(1.5)"]},
    "stocksTrans": {"name": "Stocks, Transactions and Other Flows",
               "codelists": ["ESTAT:CL_NA_STO(1.16.0)", "ESTAT:CL_NA_STO93(1.4)"]},
    "obsStatus": {"name": "Observation status", "codelists": ["SDMX:CL_OBS_STATUS(2.2)", "ESTAT:CL_OBS_STATUS(2.3)"]},
    "products": {"name": "Products", "codelists": ["ESTAT:CL_PRODUCT(1.3)", "IAEG-SDGs:CL_PRODUCT(1.19)"]},
    "institutSec": {"name": "Institutional sector", "codelists": ["ESTAT:CL_SECTOR93(1.4)", "ESTAT:CL_SECTOR(1.14)"]},
    "unitMeasure": {"name": "Units of Measurement", "codelists": ["UNSD:CL_UNIT_MEASURE(1.0)", "IMF:CL_UNIT(1.18.0)",
                                                          "ESTAT:CL_UNIT(1.3)", "IAEG-SDGs:CL_UNIT_MEASURE(1.17)"]},

    "occupation": {"name": "Occupation", "codelists": ["IAEG-SDGs:CL_OCCUPATION(1.8)", "SDMX:CL_OCCUPATION(1.0)"]},  # Codes do not overlap
    "sex": {"name": "Sex", "codelists": ["SDMX:CL_SEX(2.1)", "IAEG-SDGs:CL_SEX(1.1)"]},
    "expenditureCoipop": {"name": "Individual Consumption to Purpose",
                    "codelists": ["SDMX:CL_COICOP_1999(1.1)", "SDMX:CL_COICOP_2018(1.0)", "ESTAT:CL_COICOP(2.0)"]},
    "statUnit": {"name": "Statistical unit", "codelists": ["OECD:CL_STAT_UNIT(1.0)", "UIS:CL_STAT_UNIT(1.0)"]},

    "educationLev": {"name": "Education Level", "codelists": ["UIS:CL_EDUCATION_LEVEL(1.0)", "IAEG-SDGs:CL_EDUCATION_LEV(1.10)"]},
    "lands": {"name": "Lands", "codelists": ["ESTAT:CL_LAND_COVER(1.0)", "ESTAT:CL_LAND_USE(1.0.1)"]},
    "timePerCollect": {"name": "Time Period Collection", "codelists": ["IMF:CL_TIME_COLLECT(1.0)", "SDMX:CL_TIME_PER_COLLECT(1.0)"]},
    "transformation": {"name": "Time series transformation", "codelists": ["ESTAT:CL_TRANSFORMATION(1.4)", "SDMX:CL_TIMETRANS(1.0)"]},
    "workStatus": {"name": "Activity and employment status", "codelists": ["ESTAT:SCL_CL_WSTATUS(1.0)", "ESTAT:SCL_WSTATUS(1.0)"]},
    "urbanisation": {"name": "Degree of urbanisation", "codelists": ["SDMX:CL_DEG_URB(1.0)", "IAEG-SDGs:CL_URBANISATION(1.10)"]},
    "expenditureCofog": {"name": "Functions of Government",
              "codelists": ["ESTAT:CL_COFOG(1.0)", "SDMX:CL_COFOG_1999(1.0)"]},  # Small overlap
    "expenditureCopni": {"name": "Purposes of Non-Profit Institutions Serving Households",
                  "codelists": ["ESTAT:CL_COPNI(1.0)", "SDMX:CL_COPNI_1999(1.0)"]},
    "expenditureCopp": {"name": "Outlays of Producers According to Purpose",
                 "codelists": ["ESTAT:CL_COPP(1.0)", "SDMX:CL_COPP_1999(1.0)"]},

    # Difficult decision - ~1000 codes, 90 overlaps, 30 duplicates
    "itemStocks": {"name": "Items of Stocks, Transactions and Other Flows", "codelists": ["IMF:CL_ACCOUNTS_ITEM(1.8.0)", "ESTAT:CL_SEEA_STO(1.2)",
                                                            "IMF:CL_FSENTRY(1.1)"]}
}
