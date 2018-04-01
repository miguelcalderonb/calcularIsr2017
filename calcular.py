from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree as ET

mypath = "./recibosNomina"
xmlNames = []
total = 0.0
datosXml = []
isr = 0.0
isrTablaMensual = [
    {"limiteInferior": 0.01 ,"limiteSuperior": 496.07, "cuotaFija": 0.00, "porciento": 1.92},
    {"limiteInferior": 496.08,"limiteSuperior": 4210.41, "cuotaFija": 9.52, "porciento": 6.40},
    {"limiteInferior": 4210.42,"limiteSuperior": 7399.42, "cuotaFija": 247.24, "porciento": 10.88},
    {"limiteInferior": 7399.43,"limiteSuperior": 8601.50, "cuotaFija": 594.21, "porciento": 16.00},
    {"limiteInferior": 8601.51,"limiteSuperior": 10298.35, "cuotaFija": 786.54, "porciento": 17.92},
    {"limiteInferior": 10298.36,"limiteSuperior": 20770.29, "cuotaFija": 1090.61, "porciento": 21.36},
    {"limiteInferior": 20770.30,"limiteSuperior": 32736.83, "cuotaFija": 3327.42, "porciento": 23.52},
    {"limiteInferior": 32736.84,"limiteSuperior": 62500.00, "cuotaFija": 6141.95, "porciento": 30.00},
    {"limiteInferior": 62500.01,"limiteSuperior": 83333.33, "cuotaFija": 15070.90, "porciento": 32.00},
    {"limiteInferior": 83333.34,"limiteSuperior": 250000.00, "cuotaFija": 21737.57, "porciento": 34.00},
    {"limiteInferior": 250000.01,"limiteSuperior": 10000000000000000000.00, "cuotaFija": 78404.23, "porciento": 35.00}
]

isrTablaAnual = [
    {"limiteInferior": 0.01 ,"limiteSuperior": 5952.84, "cuotaFija": 0.00, "porciento": 1.92},
    {"limiteInferior": 5952.85,"limiteSuperior": 50524.92, "cuotaFija": 114.29, "porciento": 6.40},
    {"limiteInferior": 50524.93,"limiteSuperior": 88793.04, "cuotaFija": 2966.91, "porciento": 10.88},
    {"limiteInferior": 88793.05,"limiteSuperior": 103218.00, "cuotaFija": 7130.48, "porciento": 16.00},
    {"limiteInferior": 103218.01, "limiteSuperior": 123580.20, "cuotaFija": 9438.47, "porciento": 17.92},
    {"limiteInferior": 123580.21,"limiteSuperior": 249243.48, "cuotaFija": 13087.37, "porciento": 21.36},
    {"limiteInferior": 249243.49,"limiteSuperior": 392841.96, "cuotaFija": 39929.05, "porciento": 23.52},
    {"limiteInferior": 392841.97,"limiteSuperior": 750000.00, "cuotaFija": 73703.41, "porciento": 30.00},
    {"limiteInferior": 750000.01,"limiteSuperior": 1000000.00, "cuotaFija": 180850.82, "porciento": 32.00},
    {"limiteInferior": 1000000.01,"limiteSuperior": 3000000.00, "cuotaFija": 260850.81, "porciento": 34.00},
    {"limiteInferior": 3000000.01, "limiteSuperior": 10000000000000000000.00, "cuotaFija": 940850.81, "porciento": 35.00},
]

def calcularISRAnual(total, isrTabla):
    isr = 0.0
    for nivelIsr in isrTabla:
        if total > nivelIsr["limiteInferior"] and total <= nivelIsr["limiteSuperior"]:
            isr = (((total - nivelIsr["limiteInferior"]) / 100)*nivelIsr["porciento"])+nivelIsr["cuotaFija"]
    return isr

#Get the names of the files
for f in listdir(mypath):
    if ".xml" in f:
        xmlNames.append(f)

#Parse each file
for xml in xmlNames:
    tree = ET.parse(mypath+'/'+xml)
    root = tree.getroot()
    
    try:
        #Version 3.3
        if root.attrib['Version']:
            ns = {'nomina12': 'http://www.sat.gob.mx/nomina12', 'cfdi': 'http://www.sat.gob.mx/cfd/3'}

            complemento = root.find('cfdi:Complemento', ns)

            nomina = complemento.find('nomina12:Nomina', ns)
            percepciones = nomina.find('nomina12:Percepciones', ns)
            deducciones = nomina.find('nomina12:Deducciones', ns)

            isrXml = 0.0
            totalXml = 0.0

            for deduccion in deducciones.findall('nomina12:Deduccion', ns):
                if deduccion.attrib["Concepto"] == "ISR":
                    isrXml = float(deduccion.attrib["Importe"])
            
            totalXml = float(percepciones.attrib["TotalGravado"])
            total += totalXml
            isr += isrXml
            datosXml.append({"nombreArchivo": xml, "total": totalXml, "fechaPago": nomina.attrib["FechaPago"], "isrPagado": isrXml, "isrAPagar": calcularISRAnual(totalXml, isrTablaMensual)})
    except KeyError as key:
        #Version 3.2        
        ns = {'nomina': 'http://www.sat.gob.mx/nomina', 'cfdi': 'http://www.sat.gob.mx/cfd/3'}
        complemento = root.find('cfdi:Complemento', ns)

        try:
            nomina = complemento.find('nomina:Nomina', ns)
            percepciones = nomina.find('nomina:Percepciones', ns)
            deducciones = nomina.find('nomina:Deducciones', ns)

            isrXml = 0.0
            totalXml = 0.0

            if deducciones is not None:
                for deduccion in deducciones.findall('nomina:Deduccion', ns):
                    if deduccion.attrib["Concepto"] == "ISR":
                        isrXml = float(deduccion.attrib["Importe"])

            isr += isrXml
            
            totalXml = float(percepciones.attrib["TotalGravado"])
            total += totalXml
            datosXml.append({"nombreArchivo": xml,"total": totalXml, "fechaPago": nomina.attrib["FechaPago"], "isrPagado": isrXml, "isrAPagar": calcularISRAnual(totalXml, isrTablaMensual)})
        except AttributeError as key:
            #Version 3.2 con Nomina 1.2
            ns = {'nomina12': 'http://www.sat.gob.mx/nomina12', 'cfdi': 'http://www.sat.gob.mx/cfd/3'}
            nomina = complemento.find('nomina12:Nomina', ns)
            percepciones = nomina.find('nomina12:Percepciones', ns)
            deducciones = nomina.find('nomina12:Deducciones', ns)

            isrXml = 0.0
            totalXml = 0.0

            if deducciones is not None:
                for deduccion in deducciones.findall('nomina12:Deduccion', ns):
                    if deduccion.attrib["Concepto"] == "ISR":
                        isrXml = float(deduccion.attrib["Importe"])

            isr += isrXml
            totalXml = float(percepciones.attrib["TotalGravado"])
            total += totalXml

            datosXml.append({"nombreArchivo": xml,"total": totalXml, "fechaPago": nomina.attrib["FechaPago"], "isrPagado": isrXml, "isrAPagar": calcularISRAnual(totalXml, isrTablaMensual)})


#Print the results
print(" ")
print("Totales")
print(" ")
print("--------------------------------------------------------")
print("Total Calculado:     "+str(total))
print("ISR Pagado:          "+str(isr))
print("ISR Anual Calculado: "+str(calcularISRAnual(total, isrTablaAnual)))
print("--------------------------------------------------------")

print("")
print("Desglose por Comprobante")
print("")

for xml in datosXml:
    print("--------------------------------------------------------")
    print("Nombre Archivo  "+str(xml["nombreArchivo"]))
    print("FechaPago       "+str(xml["fechaPago"]))
    print("Total:          "+str(xml["total"]))
    print("ISR Pagado:     "+str(xml["isrPagado"]))
    print("ISR Calculado:  "+str(xml["isrAPagar"]))
    print("--------------------------------------------------------")