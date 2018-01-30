let canvas
let context
let blobs = []

function start() {
    canvas = document.createElement('canvas')
    canvas.id = 'canvas'
    canvas.style.backgroundColor = '#333'

    context = canvas.getContext('2d')
    
    document.body.style.padding = '0'
    document.body.style.margin = '0'
    canvas.style.paddingLeft = 'auto'
    canvas.style.paddingLeft = 'auto'

    resize_canvas()
    document.body.appendChild(canvas)

    for (let i = 0; i < 60; i++) blobs.push(new Blob(true))
    for (let i = 0; i < 40; i++) blobs.push(new Blob(false))

    draw()
}

function resize_canvas() {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
}

function  draw() {
    context.setTransform(1, 0, 0, 1, 0, 0)
    context.translate(canvas.width / 2, canvas.height / 2)
    
    context.fillStyle = '#4c6'
    context.beginPath()
    context.rect(-canvas.width / 2, canvas.height / 2, canvas.width, -canvas.height)
    context.arc(0, 0, 400, 0, 2 * Math.PI)
    context.fill()

    blobs.forEach(blob => {blob.draw(context)})
}

window.onload = start
window.onresize = resize_canvas