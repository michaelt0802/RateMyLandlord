// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        rows: [],
        // Form fields
        reviews_contents: "",
        reviews_property_address: "",
        reviews_score_overall: "",
        reviews_score_responsiveness: "5",
        reviews_score_friendliness: "5",
        // End form fields
        add_mode: false,
        can_delete: false,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };



    app.delete_post = function(row_idx){
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_reviews_url, {params: {id: id}}).then(function(response){
            for(let i=0; i<app.vue.rows.length; i++){
                if(app.vue.rows[i].id == id){
                    app.vue.rows.splice(i, 1);
                    app.enumerate(app.vue.rows);
                    break;
                }
            }
        });
    }



    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        delete_post: app.delete_post,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(load_reviews_url).then(function (response) {
            app.vue.rows = app.enumerate(response.data.rows);
        });
        
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
