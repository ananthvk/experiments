import { buildSchema, graphql } from "graphql";

const schema = buildSchema(
    `
    type Query {
        hello: String
    }
    `
)

const rootValue = {
    hello() {
        return "Hello there"
    }
}

graphql({
    schema,
    source: '{hello}',
    rootValue
}).then((response) => {
    console.log(JSON.stringify(response, null, 2))
})