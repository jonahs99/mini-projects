let canvas
let context
let entities
let environment

let log_history = []
let log_buffer = {best: 0, average: 0, n: 0}

let draw_vision = false
let entity_draw = {
    agent: (agent) => {
        context.save()
        context.translate(agent.pos[0], agent.pos[1])
        context.rotate(agent.dir)
        context.fillStyle = '#28e'
        context.beginPath()
        context.arc(agent.rad * 0.8, 0, agent.rad * 0.5, 0, 2 * Math.PI)
        context.fill()
        context.fillStyle = '#06d'
        context.beginPath()
        context.arc(0, 0, agent.rad, 0, 2 * Math.PI)
        context.fill()

        if (draw_vision) {
            for (let i = 0; i < agent.eye_dist.length; i++) {
                ang = agent.fov / agent.eye_dist.length * 2 * i - agent.fov
                context.rotate(ang)
                let r = Math.floor(agent.eye_r[i] * 200 + 20)
                let g = Math.floor(agent.eye_g[i] * 200)
                let b = 20
                let a = agent.eye_decay[i]
                context.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ','  + a + ')'
                context.strokeStyle = '#eee'
                context.lineWidth = 1
                context.beginPath()
                context.arc(agent.eye_dist[i], 0, 4, 0, Math.PI * 2)
                context.fill()
                context.stroke()
                /*context.lineWidth = 2
                context.beginPath()
                context.moveTo(0, 0)
                context.lineTo(agent.eye_dist[i], 0)
                context.stroke()*/
                context.rotate(-ang)
            }
        }

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
        environment = data.environment
        entities = data.entities
        log_fitness()
        draw()
    })
    setInterval(sample_log, 1000)
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

function log_fitness() {
    best = -100
    avg = 0
    n = 0
    entities.forEach((e) => {
        if (e && e.type == 'agent') {
            avg += e.fitness
            if (e.fitness > best) best = e.fitness
            n++
        }
    })
    if (n === 0) return
    avg /= n

    log_buffer.best += best
    log_buffer.average += avg
    log_buffer.n++
}

function sample_log() {
    log_history.push({best: log_buffer.best / log_buffer.n, average: log_buffer.average / log_buffer.n})

    log_buffer.best = 0
    log_buffer.average = 0
    log_buffer.n = 0
}

function draw() {
    context.setTransform(1, 0, 0, 1, 0, 0)
    context.clearRect(0, 0, canvas.width, canvas.height)
    context.translate(100 + environment.rad, canvas.height / 2)
    
    draw_bg()
    draw_entities()
    draw_log()
}

function draw_bg() {
    context.fillStyle = '#4c6'
    context.strokeStyle = '#4c6'
    context.lineWidth = 4
    context.beginPath()
    //context.rect(-canvas.width / 2, canvas.height / 2, canvas.width, -canvas.height)
    context.arc(0, 0, environment.rad, 0, 2 * Math.PI)
    context.stroke()
    //context.fill()
}

function draw_entities() {
    entities.forEach((e) => {
        if (e) entity_draw[e.type](e)
    })
}

function draw_log() {
    if (log_history.length < 2) return
    spacing = environment.rad * 1.5 / (log_history.length - 1)

    context.beginPath()
    context.moveTo(environment.rad + 100, 0)
    for (let i = 0; i < log_history.length; i++) {
        lh = log_history[i]
        context.lineTo(environment.rad + 100 + i * spacing, -10 * lh.best)
    }
    context.strokeStyle = '#4c6'
    context.lineWidth = 2
    context.stroke()

    context.beginPath()
    context.moveTo(environment.rad + 100, 0)
    for (let i = 0; i < log_history.length; i++) {
        lh = log_history[i]
        context.lineTo(environment.rad + 100 + i * spacing, -10 * lh.average)
    }
    context.strokeStyle = '#d05'
    context.lineWidth = 2
    context.stroke()
}

window.onload = start
window.onresize = resize_canvas