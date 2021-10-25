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
        reviews_landlordID: 0,
        reviews_contents: "",
        reviews_property_address: "",
        reviews_score_overall: "",
        reviews_score_responsiveness: "5",
        reviews_score_friendliness: "5",
        // End form fields
        add_mode: false,
        can_delete: false,

        r_value: 5,
        f_value: 5,
        count: 0,

    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.complete = (reviews) => {
        reviews.map((review) => {
            review.voted = 0;
            review.vote_display = 0;
        })
    };

    app.set_add_status = function(new_status){
        var x = document.getElementById("plus");
        app.vue.add_mode = new_status;
        /*if(new_status == true){
            x.style.visibility = 'hidden';
        }
        else{
            x.style.visibility = 'visible';
        }*/
        //app.vue.init_autofill();
    

        /*let input = document.getElementById('searchTextField');
        let autocomplete = new google.maps.places.Autocomplete(input);
        google.maps.event.addListener(autocomplete, 'place_changed', function () {
            var place = autocomplete.getPlace();
            document.getElementById('city2').value = place.name;
            document.getElementById('cityLat').value = place.geometry.location.lat();
            document.getElementById('cityLng').value = place.geometry.location.lng();
        });

        google.maps.event.addDomListener(window, 'load', initialize); */
       
    };

    app.add_post = function(){
        axios.post(add_reviews_url,
            {
                reviews_contents: app.vue.reviews_contents,
                reviews_landlordID: app.vue.reviews_landlordID,
                reviews_score_responsiveness: app.vue.reviews_score_responsiveness,
                reviews_score_friendliness: app.vue.reviews_score_friendliness,
                reviews_property_address: app.vue.reviews_property_address

            }).then(function (response) {
            app.vue.rows.push({
                id: response.data.id,
                reviews_landlordID: response.data.reviews_landlordID,
                reviews_contents: response.data.reviews_contents,
                reviews_property_address: response.data.reviews_property_address,
                reviews_score_responsiveness: response.data.reviews_score_responsiveness,
                reviews_score_friendliness: response.data.reviews_score_friendliness,
                renter_email: response.data.renter_email,
                reviews_score_overall: response.data.reviews_score_overall,
                renter_name: response.data.renter_name,
            });
            app.enumerate(app.vue.rows);
            app.reset_form();
            app.set_add_status(false);
        });
    };


    app.reset_form = function (){
        app.vue.add_content = "";
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

    app.init_autofill = function(){
        var input = document.getElementById('searchTextField');
        var autocomplete = new google.maps.places.Autocomplete(input);
        google.maps.event.addListener(autocomplete, 'place_changed', function () {
            var place = autocomplete.getPlace();
            document.getElementById('city2').value = place.name;
            document.getElementById('cityLat').value = place.geometry.location.lat();
            document.getElementById('cityLng').value = place.geometry.location.lng();
        });
        google.maps.event.addDomListener(window, 'load', initialize);
    }

    app.change_r_value = function(){
        let slider = document.getElementById("rep_scale");
        
        app.vue.r_value = slider.value;
    };

    app.change_f_value = function(){
        let slider = document.getElementById("friend_scale");
        
        app.vue.f_value = slider.value;
    };


    app.votes_hover = function(review_idx, vote_status){
        let review = app.vue.rows[review_idx];
        review.vote_display = vote_status;

        axios.get(get_voters_url, {params: {review_id: review.id}})
        .then((response) => {
            count = response.data.count;
            Vue.set(review, 'count', count);
        });
    };


    app.set_votes = function(review_idx, vote_status){
        let review = app.vue.rows[review_idx];

        if(vote_status !== review.voted){
            review.voted = vote_status;
        }
        else{
            review.voted = 0;
        }

        axios.post(set_votes_url, {review_id: review.id, voted: review.voted});
        axios.get(get_voters_url, {params: {review_id: review.id}})
        .then((response) => {
            count = response.data.count;
            Vue.set(review, 'count', count);
        });

    };


    app.load_count = function(review){
        axios.get(get_voters_url, {params: {review_id: review.id}})
        .then((response) => {
            count = response.data.count;
            Vue.set(review, 'count', count);
        });
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        add_post: app.add_post,
        reset_form: app.reset_form,
        set_add_status: app.set_add_status,
        delete_post: app.delete_post,
       // init_autofill: app.init_autofill,
        change_r_value: app.change_r_value,
        change_f_value: app.change_f_value,

        votes_hover: app.votes_hover,
        set_votes: app.set_votes,
        load_count: app.load_count
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = (review_id) => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(load_reviews_url).then(function (response) {
            let r = app.enumerate(response.data.rows);
            app.enumerate(r);
            app.complete(r);
            app.vue.rows = r;
        })
        .then(() => {
            for(let review of app.vue.rows) {
                app.load_count(review);
                axios.get(get_votes_url, {params: {"review_id": review.id}})
                    .then((result) => {
                        review.voted = result.data.voted;
                        review.vote_display = result.data.voted;
                    });
            }
        });
        
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
