# Error analysis: results/A3/test/run1

24 of 35 questions scored below 1.0. Label the cause of each by hand.

Causes: `wrong entity`, `wrong property`, `wrong direction`, `missing aggregation`, `wrong ORDER BY / LIMIT`, `wrong answer shape`, `other`

## ck25:1-en (F1 0.67)

**Question:** In which department is Ms. Brant?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?result WHERE {
  VALUES ?brant { prodi:empl-Karen.Brant%40company.org prodi:empl-Sylvester.Brant%40company.org }
  ?brant pv:memberOf ?result .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:11-en (F1 0.80)

**Question:** Which departments have Transducer Experts?

```sparql
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?department WHERE {
  VALUES ?product { 
    prodi:hw-T341-6404509
    prodi:hw-E709-4829800
    prodi:hw-M133-5945489
  }
  ?product pv:hasProductManager ?manager .
  ?manager pv:memberOf ?department .
}
```

**Guardrails at the end:** all passed
**Repairs:** 2

**Cause:** _________

## ck25:13-en (F1 0.00)

**Question:** How many suppliers do we have in France?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (COUNT(DISTINCT ?supplier) AS ?result) WHERE {
  VALUES ?franceSupplier { prodi:suppl-9e95d78d-7f95-4752-9e1f-d522e67e63d7 prodi:suppl-1ee8f22a-1460-4875-b1a8-89d7cb2607d6 prodi:suppl-092bb1b2-b39f-4521-9c21-c853db9d9a09 }
  ?supplier a pv:Supplier ;
              pv:country "France" .
  FILTER(?supplier = ?franceSupplier)
}
```

**Guardrails at the end:** all passed
**Repairs:** 1

**Cause:** _________

## ck25:14-en (F1 0.00)

**Question:** Which supplier in France delivers Compensators?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?result WHERE {
  ?product a pv:Hardware ; pv:hasCategory <http://ld.company.org/prod-instances/prod-cat-Compensator> ; pv:hasSupplier ?supplier .
  ?supplier pv:country "France" .
  ?supplier pv:name ?result .
}
```

**Guardrails at the end:** G7 plausibility: the query is valid but returns nothing. Check entity IRIs and direction of properties.
**Repairs:** 2

**Cause:** _________

## ck25:18-en (F1 0.00)

**Question:** What is the cheapest Oscillator we have?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result WHERE {
  ?oscillator a pv:Hardware ;
              pv:hasCategory prodi:prod-cat-Oscillator ;
              pv:price ?price .
  ?price pv:amount ?amount .
} ORDER BY ?amount LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:19-en (F1 0.00)

**Question:** What is the most expensive service we offer?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result WHERE {
  ?service a pv:Service ;
           pv:price ?price .
  ?price pv:amount ?amount .
} ORDER BY DESC(?amount) LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:21-en (F1 0.00)

**Question:** What is the heaviest coil that does not exceed a base area of 15x15 milimeter?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result WHERE {
  ?coil a pv:Hardware ;
          pv:hasCategory prodi:prod-cat-Coil ;
          pv:width_mm ?width ;
          pv:depth_mm ?depth ;
          pv:weight_g ?weight .
  FILTER(?width * ?depth <= 15 * 15)
} ORDER BY DESC(?weight) LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:23-en (F1 0.00)

**Question:** What products can I get from US suppliers that are compatible with the U990 LCD Inductor?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?result WHERE {
  ?product pv:hasSupplier ?supplier .
  ?supplier pv:country "US" .
  ?product pv:compatibleProduct prodi:hw-U990-5234138 .
}
```

**Guardrails at the end:** G7 plausibility: the query is valid but returns nothing. Check entity IRIs and direction of properties.
**Repairs:** 2

**Cause:** _________

## ck25:24-en (F1 0.00)

**Question:** What is the pontiometer with the smallest volume?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result WHERE {
  ?poti a pv:Hardware ;
          pv:hasCategory prodi:prod-cat-Potentiometer ;
          pv:depth_mm ?depth ;
          pv:height_mm ?height ;
          pv:width_mm ?width .
  BIND(?depth * ?height * ?width AS ?volume)
} ORDER BY ASC(?volume) LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:25-en (F1 0.00)

**Question:** Which coil has the highest density?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result WHERE {
  ?coil a pv:Hardware ; pv:hasCategory prodi:prod-cat-Coil ; pv:weight_g ?weight ; pv:depth_mm ?depth ; pv:height_mm ?height ; pv:width_mm ?width .
  BIND(?weight / (?depth * ?height * ?width) AS ?density)
} ORDER BY DESC(?density) LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 1

**Cause:** _________

## ck25:27-en (F1 0.76)

**Question:** Give me a phone directory of everyone on staff who does not manage anyone, I need name, email, and phone, sorted by name?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?name ?email ?phone WHERE {
  ?employee a pv:Employee .
  FILTER NOT EXISTS { ?manager pv:hasDirectReport ?employee }
  ?employee pv:name ?name ;
            pv:email ?email ;
            pv:phone ?phone .
} ORDER BY ?name
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:30-en (F1 0.00)

**Question:** Which department have more than 5 employees? I need their names and the number of employees.

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?result (COUNT(?employee) AS ?employees) WHERE {
  ?department a pv:Department ;
              pv:name ?result ;
              pv:hasDirectReport ?employee .
} GROUP BY ?result HAVING (?employees > 5)
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:32-en (F1 0.00)

**Question:** For each supplier, what's the average price (in EUR) of what they sell, round reasonably?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?supplier (ROUND(AVG(?amount)) AS ?averagePrice) WHERE {
  ?product pv:hasSupplier ?supplier .
  ?product pv:price ?price .
  ?price pv:currency "EUR" ;
           pv:amount ?amount .
} GROUP BY ?supplier
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:33-en (F1 0.00)

**Question:** Are there departments with no manager assigned?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
ASK {
  ?dept a pv:Department .
  FILTER NOT EXISTS { ?dept pv:hasManager ?manager }
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:36-en (F1 0.00)

**Question:** Which area of expertise is most relevant among our products, what are the top three skills?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result (COUNT(?product) AS ?products) WHERE {
  ?agent a pv:Employee ;
           pv:areaOfExpertise ?result .
  ?product a pv:Product ;
             pv:hasCategory ?result .
} GROUP BY ?result ORDER BY DESC(?products) LIMIT 3
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:37-en (F1 0.00)

**Question:** For each Bill of Material, how many parts does it contain and what is the total material quantity — show me only those BOMs exceeding 600 total items and order them descending.

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?bom (COUNT(?part) AS ?numParts) (SUM(?quantity) AS ?totalQuantity)
WHERE {
  ?bom a pv:BillOfMaterial ;
         pv:hasBomPart ?bomPart .
  ?bomPart pv:hasPart ?part ;
           pv:quantity ?quantity .
}
GROUP BY ?bom
HAVING (?totalQuantity > 600)
ORDER BY DESC(?totalQuantity)
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:40-en (F1 0.10)

**Question:** Which hardware items - list id and name - have no active product manager?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?id ?name WHERE {
  ?hardware a pv:Hardware ;
              pv:id ?id ;
              pv:name ?name .
  FILTER NOT EXISTS { [] pv:hasProductManager ?hardware }
}
```

**Guardrails at the end:** all passed
**Repairs:** 1

**Cause:** _________

## ck25:41-en (F1 0.00)

**Question:** For each manager, what percentage of their entire team work in the same department as the manager?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?manager (COUNT(?sameDeptEmployee) AS ?sameDeptCount) (COUNT(?allReports) AS ?totalReports) 
       ((COUNT(?sameDeptEmployee) / COUNT(?allReports)) * 100 AS ?percentage)
WHERE {
  ?manager a pv:Manager ;
             pv:hasDirectReport ?allReports .
  OPTIONAL {
    ?allReports pv:memberOf ?dept .
    ?manager pv:memberOf ?dept .
    FILTER(?allReports != ?manager)
    BIND(?allReports AS ?sameDeptEmployee)
  }
}
GROUP BY ?manager
HAVING (COUNT(?allReports) > 0)
```

**Guardrails at the end:** all passed
**Repairs:** 1

**Cause:** _________

## ck25:44-en (F1 0.20)

**Question:** Which hardware items have dimensions in the top 10 % of all widths, and what are their IDs, names and widths?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result ?id ?name ?width WHERE {
  ?hardware a pv:Hardware ;
              pv:id ?id ;
              pv:name ?name ;
              pv:width_mm ?width .
} ORDER BY DESC(?width) LIMIT 10
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:45-en (F1 0.00)

**Question:** Which supplier delivers the most reliable Inductor?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result WHERE {
  {
    SELECT (MAX(?reliability) AS ?maxReliability)
    WHERE {
      ?inductor a pv:Hardware ; 
                pv:hasCategory prodi:prod-cat-Inductor ;
                pv:reliabilityIndex ?reliability .
    }
  }
  ?inductor a pv:Hardware ; 
            pv:hasCategory prodi:prod-cat-Inductor ;
            pv:reliabilityIndex ?reliability ;
            pv:hasSupplier ?supplier .
  FILTER(?reliability = ?maxReliability)
  ?supplier pv:name ?result .
} LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 1

**Cause:** _________

## ck25:5-en (F1 0.00)

**Question:** Who has expertise in Transistors?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?result WHERE {
  ?agent a pv:Agent ;
           pv:areaOfExpertise prodi:prod-cat-Transistor .
  BIND(?agent AS ?result)
}
```

**Guardrails at the end:** G7 plausibility: the query is valid but returns nothing. Check entity IRIs and direction of properties.
**Repairs:** 2

**Cause:** _________

## ck25:7-en (F1 0.00)

**Question:** Who is the manager of the Data Services department?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result WHERE {
  ?employee pv:memberOf prodi:dept-41622 ;
            pv:hasManager ?manager .
} LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 1

**Cause:** _________

## ck25:8-en (F1 0.00)

**Question:** Which department is responsible for the Sensor Switch M558-2275045?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?result WHERE {
  prodi:hw-M558-2275045 pv:hasProductManager ?manager .
  ?manager pv:memberOf ?department .
  ?department a pv:Department ; pv:name ?result .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:9-en (F1 0.00)

**Question:** How many Sensor Switches do we offer?

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX pv: <http://ld.company.org/prod-vocab/>
PREFIX prodi: <http://ld.company.org/prod-instances/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (COUNT(DISTINCT ?sensorSwitch) AS ?result) WHERE {
  ?sensorSwitch a pv:Hardware ;
                rdfs:label "Sensor Switches" .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________
