@startuml
left to right direction
actor "User" as user
rectangle "Текстовый Редактор" {
  usecase "Проверить синтаксис"
  usecase "Редактировать" as UC1
  usecase "Печатать" as UC2
  usecase "Сохранить в разных форматах" as UC3
  usecase "Поиск по файлу" as UC4
}
user --> UC1
user --> UC2
user --> UC3
user --> UC4
@enduml

