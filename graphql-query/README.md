# Graphql programs

## Findings

1. Aliases

```
{ products { name id idCPy: id }  }
```
Graphql does not cache the results of aliases, and hence the (trivial resolver for id) is called twice, once for id and once for idCpy
So a malicious user can create an attack by creating multiple aliases of the same field. 
Even though the underlying data is the same, GraphQL fetches it multiple times.

2. The trivial resolver (for id) is called even after a mutation
```
mutation {
    addProduct(product: {name: "Laptop"}) {
        name
        id
    }
}
```
This is because the mutation returns data, and that returned data is resolved like a query
