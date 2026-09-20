# Error analysis: results/A3/test/run1

30 of 35 questions scored below 1.0. Label the cause of each by hand.

Causes: `wrong entity`, `wrong property`, `wrong direction`, `missing aggregation`, `wrong ORDER BY / LIMIT`, `wrong answer shape`, `other`

## ck25:10-en (F1 0.00)

**Question:** What is the name of the Network expert from the Marketing Department?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?result WHERE {
  ?networkExpert a pv:Hardware ; pv:name "Network expert" .
  ?networkExpert pv:memberOf <http://ld.company.org/prod-instances/dept-85880> .
  BIND(?networkExpert AS ?result)
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:11-en (F1 0.00)

**Question:** Which departments have Transducer Experts?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?department WHERE {
  ?employee a pv:Employee ; pv:areaOfExpertise <http://ld.company.org/prod-instances/hw-T341-6404509> .
  ?manager a pv:Manager ; pv:hasDirectReport ?employee .
  ?department a pv:Department ; pv:responsibleFor ?product .
  ?product a pv:Product ; pv:hasProductManager ?manager ;
    pv:compatibleProduct <http://ld.company.org/prod-instances/hw-T341-6404509> .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:13-en (F1 0.00)

**Question:** How many suppliers do we have in France?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT (COUNT(DISTINCT ?supplier) AS ?result) WHERE {
  ?supplier a pv:Supplier ; pv:country <http://ld.company.org/prod-instances/suppl-9e95d78d-7f95-4752-9e1f-d522e67e63d7> .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:14-en (F1 0.00)

**Question:** Which supplier in France delivers Compensators?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?supplier WHERE {
  ?product a pv:Hardware ; pv:name "LCD Compensator" .
  ?bom pv:hasPart [ pv:part ?product ] ;
        pv:hasSupplier ?supplier .
  ?supplier pv:country "France" .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:17-en (F1 0.00)

**Question:** Which suppliers do we have in Toulouse?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?result WHERE {
  ?supplier a pv:Supplier ; pv:addressLocality "Toulouse" .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:18-en (F1 0.00)

**Question:** What is the cheapest Oscillator we have?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?result WHERE {
  ?oscillator a pv:Hardware ; pv:name "Oscillator" ;
    pv:price [ pv:amount ?amount ; pv:currency "EUR" ] .
  FILTER(?amount = (SELECT MIN(?amount) WHERE {
    ?otherOscillator a pv:Hardware ; pv:name "Oscillator" ;
      pv:price [ pv:amount ?amount ; pv:currency "EUR" ] .
  }))
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:19-en (F1 0.00)

**Question:** What is the most expensive service we offer?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?result WHERE {
  ?service a pv:Service ;
           pv:price ?price .
  ?price pv:amount ?amount ;
          pv:currency ?currency .
  FILTER(?amount = (SELECT MAX(?amount) WHERE { ?price2 pv:amount ?amount2 . }))
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:21-en (F1 0.00)

**Question:** What is the heaviest coil that does not exceed a base area of 15x15 milimeter?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?result WHERE {
  ?result a pv:Hardware ;
           pv:weight_g ?weight ;
           pv:areaOfExpertise pv:prod-cat-Coil .
  FILTER(?weight = (SELECT MAX(?w) FROM { ?part a pv:BomPart ; pv:hasProduct ?result ; pv:quantity ?q . BIND(?q * ?w AS ?w) }))
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:23-en (F1 0.00)

**Question:** What products can I get from US suppliers that are compatible with the U990 LCD Inductor?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?product WHERE {
  ?supplier a pv:Supplier ; pv:country "United States" .
  ?product pv:hasSupplier ?supplier ;
           pv:compatibleProduct <http://ld.company.org/prod-instances/hw-U990-5234138> .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:24-en (F1 0.00)

**Question:** What is the pontiometer with the smallest volume?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?result WHERE {
  ?pontiometer a pv:Hardware ; pv:name "pontiometer" .
  ?pontiometer pv:depth_mm ?depth ; pv:height_mm ?height ; pv:width_mm ?width .
  BIND(?depth * ?height * ?width AS ?volume) .
  ORDER BY ASC(?volume)
  LIMIT 1
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:25-en (F1 0.00)

**Question:** Which coil has the highest density?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT (MAX(?density) AS ?maxDensity) WHERE {
  ?coil a pv:Hardware ; pv:weight_g ?weight ; pv:height_mm ?height .
  BIND((?weight / (?height * ?height)) AS ?density)
} ORDER BY DESC(?maxDensity) LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:27-en (F1 0.76)

**Question:** Give me a phone directory of everyone on staff who does not manage anyone, I need name, email, and phone, sorted by name?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?name ?email ?phone WHERE {
  ?employee a pv:Employee ;
             pv:name ?name ;
             pv:email ?email ;
             pv:phone ?phone .
  FILTER NOT EXISTS { ?manager a pv:Manager ; pv:hasDirectReport ?employee } .
} ORDER BY ?name
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:30-en (F1 0.00)

**Question:** Which department have more than 5 employees? I need their names and the number of employees.

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?department (COUNT(?employee) AS ?numEmployees) WHERE {
  ?department a pv:Department ;
               pv:memberOf ?employee .
} GROUP BY ?department HAVING (?numEmployees > 5)
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:32-en (F1 0.00)

**Question:** For each supplier, what's the average price (in EUR) of what they sell, round reasonably?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?supplier (ROUND(AVG(?price)) AS ?averagePriceEUR) WHERE {
  ?product a pv:Product ; pv:hasSupplier ?supplier .
  ?price a pv:Price ; pv:currency "EUR" ; pv:amount ?amount .
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
  ?department a pv:Department ;
               pv:hasManager ?manager .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:34-en (F1 0.00)

**Question:** I need to update my supplier rolodex, give me every supplier's name and all address details.

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?supplierName ?addressCountry ?addressLocality ?addressText WHERE {
  ?supplier a pv:Supplier ;
             pv:name ?supplierName ;
             pv:addressCountryCode ?addressCountry ;
             pv:addressLocality ?addressLocality ;
             pv:addressText ?addressText .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:36-en (F1 0.00)

**Question:** Which area of expertise is most relevant among our products, what are the top three skills?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?areaOfExpertise (COUNT(?product) AS ?count) WHERE {
  ?product a pv:Product ;
            pv:hasCategory ?category ;
            pv:hasProductManager ?manager .
  ?manager pv:areaOfExpertise ?areaOfExpertise .
} GROUP BY ?areaOfExpertise ORDER BY DESC(?count) LIMIT 3
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:37-en (F1 0.00)

**Question:** For each Bill of Material, how many parts does it contain and what is the total material quantity — show me only those BOMs exceeding 600 total items and order them descending.

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?bom (COUNT(?part) AS ?partCount) (SUM(?quantity) AS ?totalQuantity) WHERE {
  ?bom a pv:BillOfMaterial ;
        pv:hasBomPart ?part .
  ?part pv:quantity ?quantity .
} GROUP BY ?bom HAVING (?totalQuantity > 600) ORDER BY DESC(?totalQuantity)
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:39-en (F1 0.00)

**Question:** Which hardware items are wider than they are tall, and have a depth under 50 mm? List their dimensions.

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?hardware (pv:width_mm(?hardware) AS ?width) (pv:height_mm(?hardware) AS ?height) (pv:depth_mm(?hardware) AS ?depth) WHERE {
  ?hardware a pv:Hardware ; pv:width_mm ?width ; pv:height_mm ?height ; pv:depth_mm ?depth .
  FILTER (?width > ?height && ?depth < 50)
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:4-en (F1 0.00)

**Question:** What is the email of Sabrina from Marketing?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?result WHERE {
  ?employee a pv:Employee ; pv:name "Sabrina" ; pv:memberOf <http://ld.company.org/prod-instances/dept-85880> .
  ?employee pv:email ?result .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:40-en (F1 0.00)

**Question:** Which hardware items - list id and name - have no active product manager?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?id ?name WHERE {
  ?hw a pv:Hardware ;
       pv:id ?id ;
       pv:name ?name .
  FILTER NOT EXISTS { ?hw pv:hasProductManager ?manager . }
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:41-en (F1 0.00)

**Question:** For each manager, what percentage of their entire team work in the same department as the manager?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?manager (COUNT(?employee) AS ?teamSize) WHERE {
  ?manager a pv:Manager ;
            pv:hasDirectReport ?employee .
} GROUP BY ?manager
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:44-en (F1 0.20)

**Question:** Which hardware items have dimensions in the top 10 % of all widths, and what are their IDs, names and widths?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?id ?name ?width_mm WHERE {
  ?hw a pv:Hardware ; pv:id ?id ; pv:name ?name ; pv:width_mm ?width_mm .
} ORDER BY DESC(?width_mm) LIMIT 10
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:45-en (F1 0.00)

**Question:** Which supplier delivers the most reliable Inductor?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?supplier (MAX(?reliabilityIndex) AS ?maxReliability) WHERE {
  ?product a pv:Hardware ; pv:name "Inductor" .
  ?bom pv:hasPart [pv:part ?product] ;
        pv:hasBomPart ?bomPart .
  ?price pv:amount ?reliabilityIndex ;
         pv:currency "EUR" .
  ?supplier pv:id ?supplierID .
} GROUP BY ?supplier ORDER BY DESC(?maxReliability) LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:47-en (F1 0.00)

**Question:** From which countries are the BOM parts of our SkySync MechWave delivered?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?country WHERE {
  <http://ld.company.org/prod-instances/bom-17> pv:hasBomPart ?bomPart .
  ?bomPart pv:hasProduct ?product .
  ?product pv:hasSupplier ?supplier .
  ?supplier pv:addressCountryCode ?country .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:5-en (F1 0.00)

**Question:** Who has expertise in Transistors?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?result WHERE {
  ?agent a pv:Agent ; pv:areaOfExpertise <http://ld.company.org/prod-instances/prod-cat-Transistor> .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:50-en (F1 0.00)

**Question:** Which department is resposible for the most product and how many product are this?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT ?department (COUNT(?product) AS ?productsCount) WHERE {
  ?product a pv:Product ; pv:responsibleFor ?department .
} GROUP BY ?department ORDER BY DESC(?productsCount) LIMIT 1
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:7-en (F1 0.00)

**Question:** Who is the manager of the Data Services department?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?result WHERE {
  <http://ld.company.org/prod-instances/dept-41622> pv:hasManager ?manager .
  ?manager a pv:Manager ;
            pv:name ?result .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:8-en (F1 0.00)

**Question:** Which department is responsible for the Sensor Switch M558-2275045?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT DISTINCT ?result WHERE {
  <http://ld.company.org/prod-instances/hw-M558-2275045> pv:responsibleFor ?result .
  ?result a pv:Department .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________

## ck25:9-en (F1 0.00)

**Question:** How many Sensor Switches do we offer?

```sparql
PREFIX pv: <http://ld.company.org/prod-vocab/>
SELECT (COUNT(DISTINCT ?sensorSwitch) AS ?result) WHERE {
  ?sensorSwitch a pv:Hardware ; pv:name "Sensor Switches" .
}
```

**Guardrails at the end:** all passed
**Repairs:** 0

**Cause:** _________
