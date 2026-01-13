import { buildSchema, graphql } from "graphql";

const schema = buildSchema(
    `
    type Query {
        products: [Product!]! 
        product(id: ID!): Product
    }
    
    type Product {
        id: ID!
        name: String!
    }
    `
)

const rootValue = {
    products: resolveProducts,
    product: resolveProduct
}

const products = [
    {
        id: "XYZ",
        name: "Toothbrush"
    },
    {
        id: "ABC",
        name: "Smartphone"
    },
    {
        id: "GHI",
        name: "Book"
    }
]

function resolveProducts() {
    console.log("resolveProducts called")
    return products
}

// Only args is passed since this is buildSchema
function resolveProduct(args) {
    console.log("resolveProduct called", args)
    return products.find(x => x.id === args.id) || null
}

graphql({
    schema,
    source: `{
        products {
            id
            name
        }
        searchedBook: product(id: "XYZ") {
            id
        }
    }`,
    rootValue
}).then((response) => {
    console.log(JSON.stringify(response, null, 2))
})