// This is code based approach

import { GraphQLID, GraphQLInputObjectType, GraphQLList, GraphQLNonNull, GraphQLObjectType, GraphQLSchema, GraphQLString } from 'graphql';
import { createHandler } from 'graphql-http/lib/use/express';
import { ruruHTML } from 'ruru/server';
import express from 'express';

let counter = 1

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

const ProductType = new GraphQLObjectType({
    name: 'Product',
    fields: () => ({
        id: {
            resolve: (obj) => { console.log('trivial resolver, resolving id for product', obj.id); return obj.id },
            type: GraphQLID,
        },
        name: {
            type: GraphQLString
        }
    })
})

const ProductInputType = new GraphQLInputObjectType({
    name: 'ProductInput',
    fields: {
        name: { type: GraphQLString }
    }
})

const schema = new GraphQLSchema({
    mutation: new GraphQLObjectType({
        name: 'Mutation',
        fields: {
            addProduct: {
                type: ProductType,
                args: {
                    product: { type: new GraphQLNonNull(ProductInputType) }
                },
                resolve: (_, { product }) => {
                    console.log("addProduct")
                    counter++
                    const newProduct = { ...product, id: "ID-" + counter }
                    products.push(newProduct)
                    return newProduct
                }
            }
        }
    }),
    query: new GraphQLObjectType({
        name: 'Query',
        fields: {
            products: {
                type: new GraphQLList(ProductType),
                resolve: () => { console.log("products resolved"); return products }
            },
            product: {
                type: ProductType,
                args: {
                    id: { type: GraphQLID }
                },
                resolve: (_, { id }) => { console.log("resolved single product (by id)"); return products.find(x => x.id === id) || null }
            }
        }
    })
})
const loggingMiddleware = (req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - IP: ${req.ip} - Status: ${res.statusCode} - ${duration}ms`);
    });
    next();
};


const app = express();
app.use(loggingMiddleware);

app.all(
    '/graphql',
    createHandler({
        schema: schema
    })
);

app.get('/', (_req, res) => {
    res.type('html');
    res.end(ruruHTML({ endpoint: '/graphql' }));
});


app.listen(5000)
console.log("Running GraphQL server at http://localhost:5000/graphql")
