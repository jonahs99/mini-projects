class Environment {

}

class Blob {
    constructor(food) {
        let rad = 40 + Math.sqrt(Math.random() * Math.pow(400 - 60, 2))
        let t = Math.random() * Math.PI * 2
        this.x = Math.cos(t) * rad
        this.y = Math.sin(t) * rad
        this.radius = Math.random() * 5 + 5
        this.fill = food ? '#cb2' : '#d05'
    }
    draw(context) {
        context.fillStyle = this.fill;
        context.beginPath()
        context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI)
        context.fill()
    }
}