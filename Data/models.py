from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Measuring(models.Model):
    """Модель для измерения"""
    user=models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор измерения",null=True)
    road_photo= models.ImageField("Изображение", null=True, upload_to="photos")
    road_width=models.FloatField("Ширина проезжей части в м",null=True)
    latitude_position= models.FloatField("Широта позиции замеряющего", null=True)
    longtiude_position= models.FloatField("Долгота позиции замеряющего", null=True)
    measurment_time = models.DateTimeField(auto_now_add=False, verbose_name="Время замера")
    measurment_duration  = models.FloatField("Продолжительность измерения (мин)", null=True)
    street_name=models.CharField(max_length=255, verbose_name="Наименование улицы",default="Не указано")
    is_deleated=models.BooleanField(verbose_name="Замеряющий запросил удаление",null=True,default=False)
    latitude_start=models.FloatField("Широта начала участка", null=True)
    longtiude_start=models.FloatField("Долгота  начала участка", null=True)
    latitude_end=models.FloatField("Широта  конца участка", null=True)
    longtiude_end=models.FloatField("Долгота конца участка", null=True)


    class Meta:
        verbose_name="Измерение"
        verbose_name_plural="Измерения"
    
    def __str__(self):
        return f"Измерение от {self.measurment_time} (автор: {self.user.username if self.user else 'Неизвестен'})"


class Transport(models.Model):
    """Модель для типов транспорта используемых в интенсивыности"""
    name = models.CharField(max_length=255,unique=True, verbose_name="Наименование транспорта",default="Не указано")

    class Meta:
        verbose_name="Тип транспорта"
        verbose_name_plural="Типы транспорта"

    def __str__(self):
        return self.name


class Intensivity(models.Model):
    """Модель для одной из частей измерения - интенсивности"""
    transport=models.ForeignKey(Transport, on_delete=models.CASCADE, verbose_name="Тип транспорта",null=True)
    measuring=models.ForeignKey(Measuring, on_delete=models.CASCADE, verbose_name="Замер",null=True)
    quanity =  models.IntegerField("Количество")

    class Meta:
        verbose_name="Интенсивность"
        verbose_name_plural="Интенсивности"

    def __str__(self):
        return f"{self.transport} - {self.quanity} (в замере {self.measuring})"

class PublicTransport(models.Model):
    """Модель для типов общественного транспорта используемых для измерения людей в общественном транспорте"""
    name = models.CharField(max_length=255,unique=True, verbose_name="Наименование общественного транспорта",default="Не указано")

    class Meta:
        verbose_name="Тип общественного транспорта"
        verbose_name_plural="Типы общественного транспорта"

    def __str__(self):
        return self.name

class PublicTransportNumber(models.Model):
    """Модель для типов номеров у общественного транспорта"""
    public_transport=models.ForeignKey(PublicTransport, on_delete=models.CASCADE, verbose_name="Тип общественного транспорта",null=True)
    number = models.CharField(max_length=4, verbose_name="Номер общественного транспорта",default="Не указано")

    class Meta:
        verbose_name="Номер общественного транспорта"
        verbose_name_plural="Номера общественного транспорта"

    def __str__(self):
        return f"{self.public_transport.name} {self.number}"

class PeopleInPublicTransport(models.Model):
    """Модель для одной из частей измерения - количества людей в общественном транспорте"""
    public_transport_number=models.ForeignKey(PublicTransportNumber, on_delete=models.CASCADE, verbose_name="Номер общественного транспорта",null=True)
    measuring=models.ForeignKey(Measuring, on_delete=models.CASCADE, verbose_name="Замер",null=True)
    sitting_place = models.FloatField("Количество сидячих мест в траспорте")
    standing_place = models.FloatField("Количество стоячих мест в траспорте")
    entering_people = models.IntegerField("Количество вошедших из траспорта людей")
    leaving_people = models.IntegerField("Количество вышедших из траспорта людей")
    time= models.DateTimeField(auto_now_add=False, verbose_name="Время прибытия транспорта")

    class Meta:
        verbose_name="Количество людей в общественном транспорте"
        verbose_name_plural="Количество людей в общественном транспорте"

    def __str__(self):
        return f"{self.public_transport.name} -  {self.time} (в замере {self.measuring})"