let canvas
let context
let entities

let entity_draw = {
    agent: (agent) => {
        context.save()
        context.translate(agent.pos[0], agent.pos[1])
        context.rotate(agent.dir)
        context.fillStyle = '#06d'
        context.beginPath()
        context.arc(0, 0, agent.rad, 0, 2 * Math.PI)
        context.arc(agent.rad * 0.8, 0, agent.rad * 0.5, 0, 2 * Math.PI)
        context.fill()
        context.restore()
    },
    blob: (blob) => {
        context.fillStyle = blob.reward > 0 ? '#cb2' : '#d05'
        context.beginPath()
        context.arc(blob.pos[0], blob.pos[1], blob.rad, 0, 2 * Math.PI)
        context.fill()
    }
}

function connect() {
    let socket = io()
    socket.on('update', (data) => {
        console.log(data)
        entities = data.entities
        draw()
    })
}

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

    connect()
}

function resize_canvas() {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
}

function draw() {
    context.setTransform(1, 0, 0, 1, 0, 0)
    context.clearRect(0, 0, canvas.width, canvas.height)
    context.translate(canvas.width / 2, canvas.height / 2)
    
    draw_bg()
    draw_entities()
}

function draw_bg() {
    context.fillStyle = '#4c6'
    context.beginPath()
    context.rect(-canvas.width / 2, canvas.height / 2, canvas.width, -canvas.height)
    context.arc(0, 0, 400, 0, 2 * Math.PI)
    context.fill()
}

function draw_entities() {
    entities.forEach((e) => {
        entity_draw[e.type](e)
    })
}

window.onload = start
window.onresize = resize_canvas