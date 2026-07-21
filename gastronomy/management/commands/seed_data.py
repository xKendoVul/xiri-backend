"""
Command para poblar la base de datos con datos de prueba.

Uso:
    python manage.py seed_data

Datos incluidos:
- 17 departamentos de Nicaragua con coordenadas
- Platillos típicos por departamento
- Rutas gastronómicas de ejemplo
"""
from django.core.management.base import BaseCommand
from gastronomy.models import Department, TraditionalFood, GastronomicRoute
from users.models import User


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de prueba de Nicaragua'

    def handle(self, *args, **options):
        self.stdout.write('Creando departamentos de Nicaragua...')
        departments = self.create_departments()
        
        self.stdout.write('Creando platillos típicos...')
        foods = self.create_traditional_foods(departments)
        
        self.stdout.write('Creando rutas gastronómicas...')
        self.create_gastronomic_routes(departments, foods)
        
        self.stdout.write(self.style.SUCCESS('¡Datos de prueba creados exitosamente!'))

    def create_departments(self):
        """Crea los 17 departamentos de Nicaragua con sus coordenadas."""
        departments_data = [
            {"name": "Boaco", "latitude": 12.4729, "longitude": -85.6604,
             "description": "Departamento caracterizado por su producción ganadera y café."},
            {"name": "Carazo", "latitude": 11.9103, "longitude": -86.2102,
             "description": "Conocido por sus bordados y textiles tradicionales."},
            {"name": "Chinandega", "latitude": 12.6298, "longitude": -87.1318,
             "description": "Zona觉得我 agrícola importante, producción de caña de azúcar."},
            {"name": "Chontales", "latitude": 11.9385, "longitude": -85.1677,
             "description": "Tierra de vaqueros y producción ganadera."},
            {"name": "Estelí", "latitude": 13.0852, "longitude": -86.3533,
             "description": "Capital del tabaco y café de altura."},
            {"name": "Granada", "latitude": 11.9294, "longitude": -85.9566,
             "description": "Ciudad colonial con riqueza gastronómica colonial."},
            {"name": "Jinotega", "latitude": 13.1042, "longitude": -86.0024,
             "description": "Departamento con mayor altitud, famoso por su café."},
            {"name": "León", "latitude": 12.4382, "longitude": -86.8784,
             "description": "Ciudad universitaria con platos típicos montañosos."},
            {"name": "Madriz", "latitude": 13.3391, "longitude": -86.5204,
             "description": "Producción de tabaco y café de alta calidad."},
            {"name": "Managua", "latitude": 12.1150, "longitude": -86.2362,
             "description": "Capital con diversidad gastronómica de todo el país."},
            {"name": "Masaya", "latitude": 11.9738, "longitude": -86.0964,
             "description": "Ciudad de los pueblos, known for mariscos and snacks."},
            {"name": "Matagalpa", "latitude": 12.9254, "longitude": -85.9189,
             "description": "Corazón del café尼加拉瓜, platos con ingredientes de altura."},
            {"name": "Nicaragua (Río San Juan)", "latitude": 11.4088, "longitude": -84.8380,
             "description": "Región tropical con Platillos acuáticos y selváticos."},
            {"name": "Nueva Segovia", "latitude": 13.6552, "longitude": -86.1184,
             "description": "Departamento三角形的，最北端 department."},
            {"name": "Rivas", "latitude": 11.4373, "longitude": -85.7136,
             "description": "Zona觉得我 costera con Platillos de mar y lago."},
            {"name": "San Juan del Norte", "latitude": 10.9488, "longitude": -83.7030,
             "description": "Zona觉得我 Caribeña con Platillos 加勒比海风格."},
            {"name": "Madriz", "latitude": 13.3391, "longitude": -86.5204,
             "description": "Tierra de mitos y leyendas con Platillos tradicionales."},
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data["name"],
                defaults={
                    "description": dept_data["description"],
                    "latitude": dept_data["latitude"],
                    "longitude": dept_data["longitude"],
                }
            )
            departments[dept.name] = dept
            if created:
                self.stdout.write(f'  - Creado: {dept.name}')
            else:
                self.stdout.write(f'  - Ya existía: {dept.name}')
        
        return departments

    def create_traditional_foods(self, departments):
        """Crea platillos típicos tradicionales de Nicaragua."""
        foods_data = [
            # León - Nacatamal
            {"name": "Nacatamal", "department": "León",
             "description": "Masa de maíz rellena de carne de cerdo, arroz, verduras y patas. Se envuelve en hojas de plátano y se cocina por varias horas.",
             "cultural_origin": "Platillo prehispánico de origen maya, base de la gastronomía nicargüense."},
            
            # León - Indio Viejo
            {"name": "Indio Viejo", "department": "León",
             "description": "Tortilla desmenuzada en caldo con carne deshilachada, tomate, chile y cebolla.",
             "cultural_origin": "Platillo de origen prehispánico, considerado uno de los más antiguos de Nicaragua."},
            
            # Managua - Vigorón
            {"name": "Vigorón", "department": "Managua",
             "description": "Yuca hervida con chicharrón y ensalada de repollo con tomate.",
             "cultural_origin": "Platillo popular Managua, originado en el barrio del mismo nombre."},
            
            # Managua - Rondón
            {"name": "Rondón", "department": "Managua",
             "description": "Sopa espesa de pescado o mariscos con tubérculos, plátano y coco.",
             "cultural_origin": "Herencia del Caribe Nicaragüense, plato de pescadores."},
            
            # Granada - Quesillo
            {"name": "Quesillo", "department": "Granada",
             "description": "Tortilla con queso frito, cebolla, crema y vinagreta.",
             "cultural_origin": "Platillo típico de la región central, snack popular en todo el país."},
            
            # Granada - Enchiladas
            {"name": "Enchiladas", "department": "Granada",
             "description": "Tortillas fritas con pollo desmenuzado, beets, huevo, queso y crema.",
             "cultural_origin": "Platillo tradicional Granadino, diferente a las enchiladas mexicanas."},
            
            # Masaya - Montuca
            {"name": "Montuca", "department": "Masaya",
             "description": "Tamales grandes de maíz con cerdo, envueltos en hojas de plátano.",
             "cultural_origin": "Platillo de origen prehispánico, popular en fiestas patronales."},
            
            # Masaya - Vaho
            {"name": "Vaho", "department": "Masaya",
             "description": "Hojaldras con quesillo, ensalada y jugo de tomate.",
             "cultural_origin": "Desayuno tradicional Masaya, variación del quesillo."},
            
            # Chinandega - Nacatamal
            {"name": "Nacatamal Noruego", "department": "Chinandega",
             "description": "Variante de nacatamal con ingredientes más elaborados.",
             "cultural_origin": "Variación local del nacatamal tradicional."},
            
            # Estelí - Tres Golpes
            {"name": "Tres Golpes", "department": "Estelí",
             "description": "Plato de frijoles, tajadas de plátano y queso frito.",
             "cultural_origin": "Desayuno típico de la región norteña."},
            
            # Jinotega - Café con Quesillo
            {"name": "Café con Quesillo", "department": "Jinotega",
             "description": "Café de altura acompañado de quesillo y pan dulce.",
             "cultural_origin": "Tradición cafetera de Jinotega."},
            
            # Matagalpa - atol de maiz nuevo
            {"name": "Atol de Maíz Nuevo", "department": "Matagalpa",
             "description": "Bebida dulce de maíz tierno molido con leche y vainilla.",
             "cultural_origin": "Bebida ceremonial de las tierras altas."},
            
            # Rivas - Lapiz
            {"name": "Lápiz", "department": "Rivas",
             "description": "Guisado de carne en salsa de tomate con arroz.",
             "cultural_origin": "Platillo típico del Pacífico Sur."},
            
            # Rivas - Arroz con leche
            {"name": "Arroz con Leche", "department": "Rivas",
             "description": "Postre de arroz cocido en leche con canela y pasas.",
             "cultural_origin": "Postre colonial español adaptado en Nicaragua."},
            
            # Chontales -起草肉
            {"name": "Carne Asada", "department": "Chontales",
             "description": "Carne de res asada con Chimichurri, arroz y frijoles.",
             "cultural_origin": "Tradición ganadera de los chontaleños."},
            
            # Boaco -起草鸡肉
            {"name": "Pollo asado", "department": "Boaco",
             "description": "Pollo asado al carbón con ensalada y tortillas.",
             "cultural_origin": "Platillo campesino tradicional."},
            
            # Carazo -起草甜食
            {"name": "Cajeta de Leche", "department": "Carazo",
             "description": "Dulce de leche cocida lentamente con vainilla.",
             "cultural_origin": "Dulce tradicional de Carazo, región conocida por lácteos."},
            
            # Nueva Segovia -起草山区
            {"name": "Pupusas de Maíz", "department": "Nueva Segovia",
             "description": "Tortillas gruesas rellenas de queso o frijoles.",
             "cultural_origin": "Influencia salvadoreña en la región norte."},
            
            # San Juan del Norte -起草加勒比
            {"name": "Rondón de Mar", "department": "San Juan del Norte",
             "description": "Rondón preparado con pulpo,-langosta y椰子.",
             "cultural_origin": "Herencia加勒比海风格 en la costa del Caribe."},
            
            # Madriz -起草传统
            {"name": "Tostadas de Maíz", "department": "Madriz",
             "description": "Tostadas crujientes de maíz con crema y queso.",
             "cultural_origin": "Snack tradicional del departamento."},
        ]
        
        foods = {}
        for food_data in foods_data:
            dept = departments.get(food_data["department"])
            if dept:
                food, created = TraditionalFood.objects.get_or_create(
                    name=food_data["name"],
                    defaults={
                        "description": food_data["description"],
                        "cultural_origin": food_data["cultural_origin"],
                        "department_origin": dept,
                    }
                )
                foods[food.name] = food
                if created:
                    self.stdout.write(f'  - Creado: {food.name} ({dept.name})')
                else:
                    self.stdout.write(f'  - Ya existía: {food.name}')
        
        return foods

    def create_gastronomic_routes(self, departments, foods):
        """Crea rutas gastronómicas de ejemplo."""
        routes_data = [
            {
                "name": "Ruta del Nacatamal",
                "department": "León",
                "description": "Recorre los mejores lugares para probar nacatamales en León.",
            },
            {
                "name": "Ruta del Quesillo",
                "department": "Granada",
                "description": "Descubre los mejores quesillos de Granada.",
            },
            {
                "name": "Ruta del Café y Sabor",
                "department": "Jinotega",
                "description": "Experimenta el café de altura con comida tradicional.",
            },
            {
                "name": "Ruta del Pacífico",
                "department": "Rivas",
                "description": "Sabores del lago y el Pacífico sur.",
            },
            {
                "name": "Ruta del Caribe Nicaragüense",
                "department": "San Juan del Norte",
                "description": "Sabores加勒比海风格 en la costa caribeña.",
            },
        ]
        
        for route_data in routes_data:
            dept = departments.get(route_data["department"])
            if dept:
                route, created = GastronomicRoute.objects.get_or_create(
                    name=route_data["name"],
                    defaults={
                        "description": route_data["description"],
                        "department": dept,
                    }
                )
                if created:
                    self.stdout.write(f'  - Creada: {route.name}')
                else:
                    self.stdout.write(f'  - Ya existía: {route.name}')
