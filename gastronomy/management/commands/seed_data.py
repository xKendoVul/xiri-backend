"""
Command para poblar la base de datos con datos de prueba.

Uso:
    python manage.py seed_data

Datos incluidos:
- 17 departamentos/regiones de Nicaragua con coordenadas
- Platillos típicos por departamento
- Rutas gastronómicas de ejemplo
"""
from django.core.management.base import BaseCommand
from gastronomy.models import Department, TraditionalFood, GastronomicRoute


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de prueba de Nicaragua'

    def handle(self, *args, **options):
        self.stdout.write('Creando departamentos de Nicaragua...')
        departments = self.create_departments()

        self.stdout.write('Creando platillos típicos...')
        foods = self.create_traditional_foods(departments)

        self.stdout.write('Creando rutas gastronómicas...')
        self.create_gastronomic_routes(departments)

        self.stdout.write(self.style.SUCCESS('\n¡Datos de prueba creados exitosamente!'))

    def create_departments(self):
        """Crea los 17 departamentos/regiones de Nicaragua con sus coordenadas."""
        departments_data = [
            {"name": "Boaco", "latitude": 12.4729, "longitude": -85.6604,
             "description": "Departamento caracterizado por su producción ganadera y café."},
            {"name": "Carazo", "latitude": 11.9103, "longitude": -86.2102,
             "description": "Conocido por sus bordados, textiles y producción láctea."},
            {"name": "Chinandega", "latitude": 12.6298, "longitude": -87.1318,
             "description": "Zona agrícola importante, producción de caña de azúcar y maní."},
            {"name": "Chontales", "latitude": 11.9385, "longitude": -85.1677,
             "description": "Tierra de vaqueros y producción ganadera."},
            {"name": "Estelí", "latitude": 13.0852, "longitude": -86.3533,
             "description": "Capital del tabaco y café de altura."},
            {"name": "Granada", "latitude": 11.9294, "longitude": -85.9566,
             "description": "Ciudad colonial con riqueza gastronómica y tradicional."},
            {"name": "Jinotega", "latitude": 13.1042, "longitude": -86.0024,
             "description": "Departamento con mayor altitud, famoso por su café."},
            {"name": "León", "latitude": 12.4382, "longitude": -86.8784,
             "description": "Ciudad universitaria con platos típicos montañosos."},
            {"name": "Madriz", "latitude": 13.3391, "longitude": -86.5204,
             "description": "Producción de tabaco y café de alta calidad."},
            {"name": "Managua", "latitude": 12.1150, "longitude": -86.2362,
             "description": "Capital con diversidad gastronómica de todo el país."},
            {"name": "Masaya", "latitude": 11.9738, "longitude": -86.0964,
             "description": "Ciudad de los pueblos, conocida por sus mariscos y snacks."},
            {"name": "Matagalpa", "latitude": 12.9254, "longitude": -85.9189,
             "description": "Corazón del café nicaragüense, platos con ingredientes de altura."},
            {"name": "Nueva Segovia", "latitude": 13.6552, "longitude": -86.1184,
             "description": "Departamento del norte, tierra de mitos y leyendas."},
            {"name": "Río San Juan", "latitude": 11.4088, "longitude": -84.8380,
             "description": "Región tropical con platillos acuáticos y selváticos."},
            {"name": "Rivas", "latitude": 11.4373, "longitude": -85.7136,
             "description": "Zona costera con platillos de mar y lago."},
            {"name": "Costa Caribe Norte", "latitude": 13.2541, "longitude": -84.8380,
             "description": "Región Caribe con gastronomía de origen afrodescendiente e indígena."},
            {"name": "Costa Caribe Sur", "latitude": 12.1389, "longitude": -83.7030,
             "description": "Región Caribe con platillos de coco, mariscos y sabor caribeño."},
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
            # León
            {"name": "Nacatamal", "department": "León",
             "description": "Masa de maíz rellena de carne de cerdo, arroz, verduras y papas. Se envuelve en hojas de plátano y se cocina por varias horas.",
             "cultural_origin": "Platillo prehispánico de origen mesoamericano, base de la gastronomía nicaragüense."},
            {"name": "Indio Viejo", "department": "León",
             "description": "Tortilla desmenuzada en caldo con carne deshilachada, tomate, chile y cebolla.",
             "cultural_origin": "Platillo de origen prehispánico, considerado uno de los más antiguos de Nicaragua."},

            # Managua
            {"name": "Vigorón", "department": "Managua",
             "description": "Yuca hervida con chicharrón y ensalada de repollo con tomate y vinagreta.",
             "cultural_origin": "Platillo popular de Managua, originado en el barrio del mismo nombre."},
            {"name": "Rondón", "department": "Managua",
             "description": "Sopa espesa de pescado o mariscos con tubérculos, plátano y leche de coco.",
             "cultural_origin": "Herencia del Caribe nicaragüense, plato de pescadores."},

            # Granada
            {"name": "Quesillo", "department": "Granada",
             "description": "Tortilla con queso frito, cebolla encurtida, crema y vinagreta.",
             "cultural_origin": "Platillo típico de la región central, snack popular en todo el país."},
            {"name": "Enchilada Nicaragüense", "department": "Granada",
             "description": "Tortilla frita con pollo desmenuzado, ensalada de remolacha, huevo, queso y crema.",
             "cultural_origin": "Platillo tradicional granadino, diferente a las enchiladas mexicanas."},

            # Masaya
            {"name": "Montucas", "department": "Masaya",
             "description": "Tamales de maíz con cerdo o pollo, envueltos en hojas de plátano.",
             "cultural_origin": "Platillo de origen prehispánico, popular en fiestas patronales."},
            {"name": "Vaho", "department": "Masaya",
             "description": "Plato a base de yuca, plátano, carne de res y repollo cocidos al vapor.",
             "cultural_origin": "Desayuno tradicional de Masaya, de origen campesino."},

            # Chinandega
            {"name": "Nacatamal de Juana", "department": "Chinandega",
             "description": "Variante regional del nacatamal con ingredientes más elaborados del Pacífico.",
             "cultural_origin": "Variación local del nacatamal tradicional."},
            {"name": "Sopa de Queso", "department": "Chinandega",
             "description": "Sopa de caldo de res con queso fresco, elote y vegetales.",
             "cultural_origin": "Platillo tradicional del Pacífico Norte."},

            # Estelí
            {"name": "Tres Golpes", "department": "Estelí",
             "description": "Plato de huevos fritos, tajadas de plátano, queso frito y gallopinto.",
             "cultural_origin": "Desayuno típico de la región norteña."},
            {"name": "Pinol", "department": "Estelí",
             "description": "Bebida de maíz tostado, cacao, pino y especias.",
             "cultural_origin": "Bebida ceremonial prehispánica de origen chorotega."},

            # Jinotega
            {"name": "Café de Altura con Quesillo", "department": "Jinotega",
             "description": "Café de altura acompañado de quesillo y pan dulce.",
             "cultural_origin": "Tradición cafetera de las tierras altas de Jinotega."},

            # Matagalpa
            {"name": "Atol de Maíz Nuevo", "department": "Matagalpa",
             "description": "Bebida dulce de maíz tierno molido con leche, canela y vainilla.",
             "cultural_origin": "Bebida ceremonial de las tierras altas del norte."},

            # Rivas
            {"name": "Arroz a la Valenciana", "department": "Rivas",
             "description": "Arroz cocido con pollo, chorizo, vegetales y especias.",
             "cultural_origin": "Platillo típico del Pacífico Sur, variante del arroz valenciano español."},
            {"name": "Arroz con Leche", "department": "Rivas",
             "description": "Postre de arroz cocido en leche con canela y pasas.",
             "cultural_origin": "Postre colonial español adaptado en Nicaragua."},

            # Chontales
            {"name": "Carne Asada", "department": "Chontales",
             "description": "Carne de res asada al carbón con chimichurri, arroz y frijoles.",
             "cultural_origin": "Tradición ganadera de los chontaleños."},

            # Boaco
            {"name": "Pollo Asado al Carbón", "department": "Boaco",
             "description": "Pollo asado al carbón con ensalada de repollo, tajadas y tortillas.",
             "cultural_origin": "Platillo campesino tradicional de Boaco."},

            # Carazo
            {"name": "Cajeta de Leche", "department": "Carazo",
             "description": "Dulce de leche cocido lentamente con vainilla y azúcar.",
             "cultural_origin": "Dulce tradicional de Carazo, región conocida por su producción láctea."},

            # Nueva Segovia
            {"name": "Pupusas de Maíz", "department": "Nueva Segovia",
             "description": "Tortillas gruesas rellenas de queso, frijoles o chicharrón.",
             "cultural_origin": "Influencia salvadoreña en la región fronteriza del norte."},

            # Río San Juan
            {"name": "Sopa de Mondongo", "department": "Río San Juan",
             "description": "Sopa de caldo de res con verduras, hierbas y acompañamientos.",
             "cultural_origin": "Platillo tradicional de la selva nicaragüense."},

            # Costa Caribe Norte
            {"name": "Wabul", "department": "Costa Caribe Norte",
             "description": "Plátano verde machacado con queso, mantequilla y leche.",
             "cultural_origin": "Platillo tradicional misquito de la Costa Caribe."},
            {"name": "Gaubul", "department": "Costa Caribe Norte",
             "description": "Bebida de plátano verde cocido con leche de coco.",
             "cultural_origin": "Bebida tradicional misquito de la Costa Caribe Norte."},

            # Costa Caribe Sur
            {"name": "Rondón de Mar", "department": "Costa Caribe Sur",
             "description": "Rondón preparado con pescado, langosta, camarones y leche de coco.",
             "cultural_origin": "Herencia afrocaribeña en la costa del Caribe Sur."},
            {"name": "Patí", "department": "Costa Caribe Sur",
             "description": "Empanada rellena de pescado sazonado, horneada o frita.",
             "cultural_origin": "Platillo típico afrocaribeño de Bluefields."},

            # Madriz
            {"name": "Tostadas de Maíz", "department": "Madriz",
             "description": "Tostadas crujientes de maíz con crema, queso y salsa.",
             "cultural_origin": "Snack tradicional del departamento de Madriz."},
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

    def create_gastronomic_routes(self, departments):
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
                "department": "Costa Caribe Sur",
                "description": "Sabores caribeños en la costa.",
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