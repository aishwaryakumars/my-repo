abstract class Vehicle {
    abstract void startEngine();
    abstract void fuelType();

    void display() {
        System.out.println("This is a vehicle.");
    }
}

class Car extends Vehicle {
    void startEngine() {
        System.out.println("Car engine started.");
    }

    void fuelType() {
        System.out.println("Car runs on petrol.");
    }
}

class ElectricCar extends Vehicle {
    void startEngine() {
        System.out.println("Electric car started.");
    }

    void fuelType() {
        System.out.println("Electric car runs on electricity.");
    }
}

public class Main {
    public static void main(String[] args) {
        Car car = new Car();
        car.startEngine();
        car.fuelType();
        car.display();

        System.out.println();

        ElectricCar eCar = new ElectricCar();
        eCar.startEngine();
        eCar.fuelType();
        eCar.display();
    }
}