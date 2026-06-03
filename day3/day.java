class Dog{
    int age;
    String species="Canis lupus familiaris";
    String name=species;
    Dog(){
        System.out.println("A dog has been created.");
    }
    Dog(String name){
        this.name = name;
        System.out.println("A dog named " + name + " has been created.");
    }
    Dog(String name, int age){
        this.age = age;
        this.name = name;
    }
    
    void bark(){
        System.out.println("Woof!");
    }
    // no top-level instance creation to avoid recursion and illegal statements
}

class day{
    public static void main(String[] args) {
        Dog dog1 = new Dog("Buddy");
        Dog dog2 = new Dog();
        System.out.println(dog1.species);
        System.out.println(dog2.species);
        dog1.bark();
        Dog dog3 = new Dog("alice", 5);
        System.out.println(dog3.name + " is " + dog3.age + " years old.");

    }
}