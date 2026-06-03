class Animal{
    String name;
    public void eat(){
        System.out.println(name + " is eating.");
    }
    void speak(){
        System.out.println(name + " is speaking.");
    }
}
class Dog extends Animal{
    String breed;
    public void  eat(){
        System.out.println(name + " is eating.");
    }
    void speak(){
        System.out.println(name + " says: Woof!");
    }
}
class Cat extends Animal{
    String color;
    public void eat(){
        System.out.println(name + " is eating.");
    }
    void speak(){
        System.out.println(name + " says: Meow!");
    }
}
class inheritance extends Animal{
    public static void main(String[] args) {
        Dog dog = new Dog();
        //dog.name = "Buddy";
        //dog.breed = "Golden Retriever";
        dog.eat();
        dog.speak();
        System.out.println();
        Cat cat = new Cat();
        //cat.name = "Whiskers";
        //cat.color = "Gray";
        cat.eat();
        cat.speak();
        inheritance obj = new inheritance();
        obj.name = "GenericAnimal";
        obj.eat();
       
    }
}